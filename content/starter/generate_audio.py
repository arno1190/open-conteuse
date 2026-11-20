#!/usr/bin/env python3
"""Pinned local Kokoro narration, a CPU engine also available in Voicebox.

No Voicebox app, voice cloning, paid service or account is used here. All six
files are staged and decoded before an immutable batch becomes selectable.
"""
import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL_DIR = ROOT / 'work/current/neural-tts'
VOICES = {'fr': ('ff_siwis', 'fr-fr', .78), 'en': ('bf_emma', 'en-gb', .84)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def run(args):
    return subprocess.run(args, check=True, capture_output=True)


def atomic_json(path, value):
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    os.replace(temp, path)


def render_plan(text, lang):
    """Group dialogue for prosody, preserving every original paragraph."""
    voice, language, speed = VOICES[lang]
    segments, pending = [], []
    def flush(pause=350):
        if pending:
            segments.append({'text': '\n\n'.join(pending), 'pause_after_ms': pause})
            pending.clear()
    for paragraph in text.split('\n\n'):
        if paragraph.startswith(('Si tu veux', 'If you like')):
            flush()
            pending.append(paragraph)
            flush(3000)
        else:
            pending.append(paragraph)
            if len(' '.join(pending).split()) >= 75:
                flush()
    flush(800)
    assert '\n\n'.join(x['text'] for x in segments) == text
    return {'voice': voice, 'language': language, 'speed': speed,
            'leading_silence_ms': 350, 'sentence_pause_seconds': .22,
            'clause_pause_seconds': .08, 'segments': segments}


def probe_audio(path):
    info = json.loads(run(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration:stream=codec_name,sample_rate,channels', '-of', 'json', str(path)]).stdout)
    stream = info['streams'][0]
    seconds = round(float(info['format']['duration']), 3)
    if not 120 < seconds < 480 or stream['channels'] != 1 or int(stream['sample_rate']) != 22050 or stream['codec_name'] != 'mp3':
        raise ValueError('Unexpected narration format or duration: ' + str(path))
    run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'null', '-'])
    return seconds, stream


def prepare_batch(catalog, directory, renderer, provenance, credits=''):
    """A failed render never changes any published file or catalogue."""
    revised = copy.deepcopy(catalog)
    revised['script_approval'] = revised['audio_approval'] = 'pending'
    assets = []
    for story in revised['stories']:
        story['script_approval'] = story['audio_approval'] = 'pending'
        for lang in ('fr', 'en'):
            z = story[lang]
            plan = render_plan(z['script'], lang)
            filename = story['id'] + '.' + lang + '.mp3'
            out = directory / filename
            renderer(plan, out)
            seconds, stream = probe_audio(out)
            assets.append({'story_id': story['id'], 'language': lang,
                'filename': filename, 'status': 'synthetic_draft_demo',
                'approval': 'pending', 'final_audio_approval': 'pending',
                'script_sha256': sha(z['script'].encode()),
                'render_plan': plan, 'render_plan_sha256': sha(canonical(plan)),
                'audio_sha256': sha(out.read_bytes()), 'bytes': out.stat().st_size,
                'duration_seconds': seconds, 'codec': stream['codec_name'],
                'sample_rate_hz': int(stream['sample_rate']), 'channels': stream['channels'],
                'engine': 'Kokoro 82M v1.0', 'voice': plan['voice']})
            print(filename, seconds, 'seconds', flush=True)
    batch_id = sha(canonical({'assets': assets, 'provenance': provenance}))[:24]
    for asset in assets:
        asset['path'] = 'content/audio/' + batch_id + '/' + asset.pop('filename')
        story = next(s for s in revised['stories'] if s['id'] == asset['story_id'])
        story[asset['language']]['preview_audio'] = asset['path']
        story[asset['language']]['preview_audio_duration_seconds'] = asset['duration_seconds']
    revised['audio_assets'] = assets
    revised['audio_generation'] = 'content/audio/' + batch_id + '/generation.json'
    revised['narration_credits'] = 'content/TTS-NOTICES.md'
    revised['preview_note'] = {
        'fr': 'Narration de démonstration par voix neurale locale. Textes révisés ; écoute finale en attente.',
        'en': 'Demonstration narration using a local neural voice. Revised stories; final listening approval pending.'}
    receipt = {'status': 'synthetic_draft_demo', 'final_audio_approval': 'pending',
        'batch_id': batch_id, 'engine': 'Kokoro 82M v1.0', 'provenance': provenance,
        'credits_sha256': sha(credits.encode()),
        'audio_assets': assets, 'human_listening_approval': 'pending',
        'physical_acoustic_validation': 'pending; digital normalization is not acoustic qualification',
        'not_device_pack': 'MP3 previews; PCM conversion and separate parent approval required for device export.'}
    (directory / 'CREDITS.txt').write_text(credits)
    atomic_json(directory / 'generation.json', receipt)
    return batch_id, revised, receipt


def verify_batch(directory, receipt):
    expected = {'generation.json', 'CREDITS.txt'}
    for asset in receipt['audio_assets']:
        filename = asset['story_id'] + '.' + asset['language'] + '.mp3'
        if asset['path'] != 'content/audio/' + receipt['batch_id'] + '/' + filename:
            raise ValueError('Invalid batch asset path')
        expected.add(filename)
        path = directory / filename
        if path.is_symlink() or not path.is_file() or sha(path.read_bytes()) != asset['audio_sha256']:
            raise ValueError('Missing or corrupt immutable recording: ' + filename)
    if {p.name for p in directory.iterdir()} != expected:
        raise ValueError('Unexpected or incomplete generation directory')
    if (directory / 'CREDITS.txt').is_symlink() or sha((directory / 'CREDITS.txt').read_bytes()) != receipt['credits_sha256']:
        raise ValueError('Missing or changed narration credits')
    if (directory / 'generation.json').is_symlink() or json.loads((directory / 'generation.json').read_text()) != receipt:
        raise ValueError('Changed generation receipt')


def publish_batch(stage, batch_id, catalog, receipt):
    """Publish complete immutable directories before switching catalogues.

    Build preflight rejects an interrupted metadata/mirror update. Previous
    audio remains available until the complete new set passes validation.
    """
    public = ROOT / 'site/content'
    verify_batch(stage, receipt)
    # Validate both existing destinations before changing either mirror.
    for parent in (HERE / 'audio', public / 'audio'):
        if (parent / batch_id).exists(): verify_batch(parent / batch_id, receipt)
    for parent in (HERE / 'audio', public / 'audio'):
        parent.mkdir(parents=True, exist_ok=True)
        dest = parent / batch_id
        if dest.exists():
            if (dest / 'generation.json').read_bytes() != (stage / 'generation.json').read_bytes():
                raise ValueError('Immutable generation collision')
        else:
            temp = parent / ('.' + batch_id + '.tmp')
            if temp.exists(): shutil.rmtree(temp)
            shutil.copytree(stage, temp)
            os.replace(temp, dest)
    shutil.copy2(HERE / 'TTS-NOTICES.md', public / 'TTS-NOTICES.md')
    shutil.copytree(HERE / 'tts-notices', public / 'tts-notices', dirs_exist_ok=True)
    for parent in (HERE, public):
        atomic_json(parent / 'audio-generation.json', receipt)
        atomic_json(parent / 'index.json', catalog)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch-engine', action='store_true')
    args = parser.parse_args()
    import numpy as np
    import onnxruntime as rt
    import soundfile as sf
    from kokoro_onnx import Kokoro
    lock = json.loads((HERE / 'tts-engine-lock.json').read_text())
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for asset in lock['assets']:
        path = MODEL_DIR / asset['name']
        if not path.exists() and args.fetch_engine:
            temp = path.with_suffix('.download')
            urllib.request.urlretrieve(asset['url'], temp)
            if sha(temp.read_bytes()) != asset['sha256']:
                temp.unlink()
                raise ValueError('Model download hash mismatch')
            os.replace(temp, path)
        if not path.exists() or sha(path.read_bytes()) != asset['sha256']:
            raise ValueError('Missing or changed model; use --fetch-engine: ' + asset['name'])
    if importlib.metadata.version('kokoro-onnx') != '0.6.1':
        raise ValueError('Use requirements-narration.txt')
    options = rt.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    session = rt.InferenceSession(str(MODEL_DIR / 'kokoro-v1.0.onnx'), sess_options=options, providers=['CPUExecutionProvider'])
    engine = Kokoro.from_session(session, str(MODEL_DIR / 'voices-v1.0.bin'))
    credits = (HERE / 'TTS-NOTICES.md').read_text()
    provenance = {'model_lock': lock, 'requirements_sha256': sha((HERE / 'requirements-narration.txt').read_bytes()),
        'credits_sha256': sha(credits.encode()),
        'generator_sha256': sha(Path(__file__).read_bytes()),
        'runtime_versions': {n: importlib.metadata.version(n) for n in ('kokoro-onnx', 'onnxruntime', 'numpy', 'soundfile', 'phonemizer', 'espeakng-loader')},
        'encoder_version': run(['ffmpeg', '-version']).stdout.decode().splitlines()[0],
        'provider': 'local CPU; no Voicebox app or cloud service used',
        'filter': 'atempo=0.85,loudnorm=I=-23:TP=-3:LRA=7', 'voices_are_presets': True}
    def render(plan, out):
        pieces = [np.zeros(round(24000 * plan['leading_silence_ms'] / 1000), dtype=np.float32)]
        for segment in plan['segments']:
            samples, rate = engine.create(segment['text'], voice=plan['voice'],
                speed=plan['speed'], lang=plan['language'],
                sentence_pause=plan['sentence_pause_seconds'], clause_pause=plan['clause_pause_seconds'])
            if rate != 24000 or not np.isfinite(samples).all() or not len(samples):
                raise ValueError('Invalid neural output')
            pieces.extend([samples, np.zeros(round(rate * segment['pause_after_ms'] / 1000), dtype=np.float32)])
        wav = out.with_suffix('.wav')
        sf.write(wav, np.concatenate(pieces), 24000, subtype='PCM_16')
        credit = 'Galia original script CC0; Kokoro 82M preset ' + plan['voice'] + ' (Apache-2.0 model). '
        if plan['language'] == 'fr-fr':
            credit += 'SIWIS: Yamagishi, Honnet, Garner, Lazaridis (2017), University of Edinburgh; https://doi.org/10.7488/ds/1705 ; CC BY 4.0. '
        credit += 'New synthetic speech; pacing/loudness processed; no endorsement. https://arno1190.github.io/open-conteuse/content/TTS-NOTICES.md'
        run(['ffmpeg', '-v', 'error', '-y', '-i', str(wav), '-map_metadata', '-1',
            '-af', provenance['filter'], '-ar', '22050', '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '96k',
            '-metadata', 'artist=Galia / Kokoro neural narration', '-metadata', 'comment=' + credit, str(out)])
        wav.unlink()
    with tempfile.TemporaryDirectory(prefix='galia-neural-', dir=MODEL_DIR) as temporary:
        stage = Path(temporary)
        batch_id, catalog, receipt = prepare_batch(json.loads((HERE / 'index.json').read_text()), stage, render, provenance, credits)
        publish_batch(stage, batch_id, catalog, receipt)
        print('Published complete neural batch:', batch_id)


if __name__ == '__main__':
    main()

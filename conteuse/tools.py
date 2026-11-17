"""Parent CLI for local content operations. No service required for import/export."""
import argparse
import json
from .imports import import_playlist, download_episode
from .studio import Studio


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default='.studio')
    sub=p.add_subparsers(dest='action',required=True)
    imp=sub.add_parser('import');imp.add_argument('destination');imp.add_argument('files',nargs='+');imp.add_argument('--title',default='Imported playlist')
    rss=sub.add_parser('download');rss.add_argument('feed_url');rss.add_argument('guid');rss.add_argument('destination')
    for name in ('inspect','approve','publish'):
        cmd=sub.add_parser(name);cmd.add_argument('source')
    export=sub.add_parser('export');export.add_argument('source');export.add_argument('destination')
    card=sub.add_parser('card');card.add_argument('uid');card.add_argument('revision')
    station=sub.add_parser('station');station.add_argument('station_id');station.add_argument('url');station.add_argument('--mime',default='audio/mpeg')
    args=p.parse_args();studio=Studio(args.root)
    if args.action=='import': result=import_playlist(args.files,args.destination,args.title)
    elif args.action=='download': result=download_episode(args.feed_url,args.guid,args.destination)
    elif args.action=='station': result=studio.approve_station(args.station_id,args.url,args.mime)
    elif args.action=='card': result=studio.assign_card(args.uid,args.revision)
    elif args.action=='export':
        from .device import check_device_pack
        check_device_pack(args.source)
        from .packages import activate
        digest=studio.inspect(args.source)['revision']
        if digest not in studio.state['approvals']:p.error('final revision must be approved')
        result=activate(args.source,args.destination,digest)
        from .packages import atomic_json
        from pathlib import Path
        atomic_json(Path(args.destination)/"cards.json",studio.state["cards"])
        atomic_json(Path(args.destination)/"stations.json",studio.state["stations"])
    else:result=getattr(studio,args.action)(args.source)
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()

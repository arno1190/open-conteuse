// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "admin_protocol.h"
#include <Arduino.h>
#include <esp_http_server.h>
#include <freertos/semphr.h>
#include <functional>
#include <map>
#include <string>
namespace admin {
// esp_http_server exposes headers before reading the body: unlike WebServer,
// no Content-Length-sized String is allocated by the SDK before our limit/auth.
class Http {
  httpd_handle_t handle = nullptr;
  httpd_req_t *request = nullptr;
  SemaphoreHandle_t mutex = nullptr;
  std::map<std::string, std::function<void()>> routes;
  String body;
  bool read = false;
  static esp_err_t dispatch(httpd_req_t *req) {
    auto self = static_cast<Http *>(req->user_ctx);
    xSemaphoreTake(self->mutex, portMAX_DELAY);
    self->request = req;
    self->body = "";
    self->read = false;
    std::string path = req->uri;
    path = path.substr(0, path.find('?'));
    if (!bodyAllowed(req->content_len, path == "/api/chunk")) {
      httpd_resp_set_hdr(req, "Connection", "close");
      self->send(413, "application/json", "{\"error\":\"body too large\"}");
    } else {
      auto route = self->routes.find(std::to_string(req->method) + path);
      if (route == self->routes.end())
        self->send(404, "application/json",
                   "{\"error\":\"unknown operation\"}");
      else
        route->second();
    }
    self->request = nullptr;
    xSemaphoreGive(self->mutex);
    return ESP_OK;
  }

public:
  String header(const char *name) {
    size_t n = httpd_req_get_hdr_value_len(request, name);
    if (n > 128)
      return "!oversized";
    if (!n)
      return "";
    char b[130];
    if (httpd_req_get_hdr_value_str(request, name, b, sizeof(b)) != ESP_OK)
      return "!invalid";
    return String(b);
  }
  String hostHeader() { return header("Host"); }
  String arg(const char *name) {
    if (std::string(name) == "plain") {
      if (!read) {
        read = true;
        std::string bytes(request->content_len, '\0');
        size_t offset = 0;
        const uint32_t began = millis();
        while (offset < bytes.size()) {
          if (bodyExpired(millis(), began)) {
            body = "";
            return body;
          }
          int got =
              httpd_req_recv(request, &bytes[offset], bytes.size() - offset);
          if (got <= 0) {
            body = "";
            return body;
          }
          offset += size_t(got);
        }
        // All protocol bodies are JSON; binary bytes are strictly base64
        // encoded.
        if (bytes.find('\0') != std::string::npos)
          return "";
        body = bytes.c_str();
      }
      return body;
    }
    size_t n = httpd_req_get_url_query_len(request);
    if (!n || n > 512)
      return "";
    char query[513], value[513];
    if (httpd_req_get_url_query_str(request, query, sizeof(query)) != ESP_OK ||
        httpd_query_key_value(query, name, value, sizeof(value)) != ESP_OK)
      return "";
    std::string decoded;
    for (size_t i = 0; value[i]; ++i) {
      char c = value[i];
      if (c == '%') {
        auto hex = [](char q) {
          return q >= '0' && q <= '9'   ? q - '0'
                 : q >= 'A' && q <= 'F' ? q - 'A' + 10
                 : q >= 'a' && q <= 'f' ? q - 'a' + 10
                                        : -1;
        };
        if (!value[i + 1] || !value[i + 2])
          return "";
        int a = hex(value[i + 1]), b = hex(value[i + 2]);
        if (a < 0 || b < 0 || (a == 0 && b == 0))
          return "";
        decoded += char(a * 16 + b);
        i += 2;
      } else
        decoded += c == '+' ? ' ' : c;
    }
    return String(decoded.c_str());
  }
  void sendHeader(const char *key, const char *value) {
    httpd_resp_set_hdr(request, key, value);
  }
  void send(int code, const char *mime, const String &value) {
    const char *status = code == 200   ? "200 OK"
                         : code == 403 ? "403 Forbidden"
                         : code == 404 ? "404 Not Found"
                         : code == 409 ? "409 Conflict"
                         : code == 413 ? "413 Content Too Large"
                         : code == 507 ? "507 Insufficient Storage"
                         : code == 500 ? "500 Internal Server Error"
                                       : "400 Bad Request";
    httpd_resp_set_status(request, status);
    httpd_resp_set_type(request, mime);
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    httpd_resp_set_hdr(request, "X-Content-Type-Options", "nosniff");
    httpd_resp_set_hdr(request, "Connection", "close");
    httpd_resp_send(request, value.c_str(), value.length());
    httpd_sess_trigger_close(handle, httpd_req_to_sockfd(request));
  }
  void on(const char *path, httpd_method_t method,
          std::function<void()> callback) {
    routes[std::to_string(method) + path] = callback;
  }
  bool begin(SemaphoreHandle_t lock) {
    mutex = lock;
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.uri_match_fn = httpd_uri_match_wildcard;
    config.max_open_sockets = 2;
    config.stack_size = 8192;
    config.recv_wait_timeout = 1;
    config.send_wait_timeout = 2;
    config.lru_purge_enable = true;
    if (httpd_start(&handle, &config) != ESP_OK)
      return false;
    for (auto method : {HTTP_GET, HTTP_POST}) {
      httpd_uri_t uri{};
      uri.uri = "/*";
      uri.method = method;
      uri.handler = dispatch;
      uri.user_ctx = this;
      if (httpd_register_uri_handler(handle, &uri) != ESP_OK) {
        stop();
        return false;
      }
    }
    return true;
  }
  void stop() {
    if (handle) {
      httpd_stop(handle);
      handle = nullptr;
    }
  }
};
} // namespace admin

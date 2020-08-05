#  (2020-08-05)


### Bug Fixes

* add test app init migration ([a3c9e25](https://github.com/logux/django/commit/a3c9e256cd12b1805b7ae1ff735b1450a4515d20))
* apply_commands types ([e6ff52d](https://github.com/logux/django/commit/e6ff52dd60ecc2f644ef8009006f17180c10773b))
* call resend with named args, close [#42](https://github.com/logux/django/issues/42) ([24e0de0](https://github.com/logux/django/commit/24e0de00bf0e6105899381c2c0a61fbc87ca731c))
* change "stack" field to "details", tests. ([0ed4804](https://github.com/logux/django/commit/0ed480456c16ccfb41474b53eb12cf03923476ed))
* channel_pattern type ([480651e](https://github.com/logux/django/commit/480651e9fe86c89cf7fd8d42d8edbf4acfbeb1d9))
* checks version ([cf7efac](https://github.com/logux/django/commit/cf7efac7d1114386289ce0283fc0331982bbd4ab))
* dispatch proto4 support, test unknownAction ([09bb4da](https://github.com/logux/django/commit/09bb4dacf959887f5b904ef718de7174ce9f0263))
* django security fixes ([c1148bb](https://github.com/logux/django/commit/c1148bba8bcc158076d41f17b1f94412dfcb7651))
* forbidden answer for sub action ([b01138d](https://github.com/logux/django/commit/b01138d49025126e9f8f412ccc1cf15765e881d1))
* missing docstring ([4e93947](https://github.com/logux/django/commit/4e939477bed0ccf66a45a23b855cbe3672cc99a7))
* pylint satisfaction ([c28c160](https://github.com/logux/django/commit/c28c16018aa2568013c48b982fb0fcef4c91b607))
* remove headers arg from Actions callbacks. close [#43](https://github.com/logux/django/issues/43) ([d529198](https://github.com/logux/django/commit/d5291981beea9578ad0bb62a86b07c14424e784d))
* reset test app migration ([0c28303](https://github.com/logux/django/commit/0c283037fb8167550191023e9456debda5873eca))
* test refactoring, cleanup ([a216c90](https://github.com/logux/django/commit/a216c90e1ae2769c24d99b64165359845d692fb4))
* tests types ([f7cf769](https://github.com/logux/django/commit/f7cf769c5dadc84af00f89ea0d7e1740ad39fcb1))
* token from cookie, cleanup. answer types extracting. rest tests. ([e7e2bfa](https://github.com/logux/django/commit/e7e2bfa9ed27dde684f805566bf77159f864d2c8))
* unsupported subprotocol format ([0004bec](https://github.com/logux/django/commit/0004beccbd9c948a362698fc18fd5ea78241b780))


### Features

* ActionCommand support for proto4 ([11a8340](https://github.com/logux/django/commit/11a83408a41ed0c082f4b9ceb227102f339f18d7))
* add 'headers' for action callbacks ([5fcbe6e](https://github.com/logux/django/commit/5fcbe6edec779a21f0af86a36e30b08337e118c9))
* add semantic_version pkg for subprotocols processing ([64f0f75](https://github.com/logux/django/commit/64f0f75853c7debe0ab32a0b1eb2c8e839059215))
* load multi type return support, resolved [#35](https://github.com/logux/django/issues/35) ([45ffeec](https://github.com/logux/django/commit/45ffeec72a4c000f70c57b9ec17274c6721de1ed))
* logux_add support for proto4 ([d2c26c1](https://github.com/logux/django/commit/d2c26c1f2bef259fa950d08f3464b6694bf21126))
* make cmd for running "logux backend tests" ([71142e5](https://github.com/logux/django/commit/71142e5a583d89bfb571a99041244f70e1f9b36b))
* new auth_func signature. ([c08fdb2](https://github.com/logux/django/commit/c08fdb24d1064073339847c059c09d607cacd5cb))
* new settings format, auth cmd, tests, readme update ([ae6cd66](https://github.com/logux/django/commit/ae6cd665a72900995fbae643bd93c41851b8abf3))
* proto4 auth support. ([f9c2067](https://github.com/logux/django/commit/f9c2067868b053b1c203afd5ed0b96fa2f37d7d5))
* require_http_methods for logux url ([b8e3cfb](https://github.com/logux/django/commit/b8e3cfb0feb36eadb68cddbadea9a11442e1d76d))
* return actions from channel. resolved [#35](https://github.com/logux/django/issues/35) ([098afaa](https://github.com/logux/django/commit/098afaad2cbc7613f941e0c5f999bc4927011111))
* SubCommand support for proto4, errors. Mypy. ([4542c73](https://github.com/logux/django/commit/4542c732da3443a3140873ea69c11d9a72e87e84))
* subprotocols support, wrongSubprotocol answer ([99acab8](https://github.com/logux/django/commit/99acab8284e0f6a30ffa170d30bb2cfb16d0a335))



#  (2020-06-06)


### Bug Fixes

* django security fixes ([c1148bb](https://github.com/logux/django/commit/c1148bba8bcc158076d41f17b1f94412dfcb7651))
* pylint satisfaction ([c28c160](https://github.com/logux/django/commit/c28c16018aa2568013c48b982fb0fcef4c91b607))
* tests types ([f7cf769](https://github.com/logux/django/commit/f7cf769c5dadc84af00f89ea0d7e1740ad39fcb1))



#  (2020-05-06)


### Bug Fixes

* pylint satisfaction ([c28c160](https://github.com/logux/django/commit/c28c16018aa2568013c48b982fb0fcef4c91b607))
* tests types ([f7cf769](https://github.com/logux/django/commit/f7cf769c5dadc84af00f89ea0d7e1740ad39fcb1))


## [0.1.1](https://github.com/logux/django/compare/0.1.0...0.1.1) (2020-04-18)

### Features

* LoguxRequest and LoguxResponse are LoguxValue now
* Type annotation refactoring
* Add `lint` (mypy, flake8) command for `make`
* Reduce requirements for `Django` and `requests`
* Add EditConfig
* Add SemVer
* Add custom `LoguxProxyException`



This project adheres to [Semantic Versioning](http://semver.org/).

# CHANGELOG


## v4.1.0 (2025-03-18)

### Bug Fixes

- Corrected some error request bodies
  ([`e003214`](https://github.com/Illustar0/ZZU.Py/commit/e003214b7109db987d018b9e18c13ca3cb8d5408))

### Documentation

- Add credits
  ([`440f50c`](https://github.com/Illustar0/ZZU.Py/commit/440f50c2a1b8762e90e604f4af63eee93ba6dedf))

- Add models.rst
  ([`9658a97`](https://github.com/Illustar0/ZZU.Py/commit/9658a97153ab8bec101288b3f28020162481d782))

- Enable sphinx to parse pydantic models
  ([`b79e726`](https://github.com/Illustar0/ZZU.Py/commit/b79e72685b7ac08a4d68c1b59b5793b981c77b53))

- Update features
  ([`2a28eba`](https://github.com/Illustar0/ZZU.Py/commit/2a28eba2a94957dd7556b37c5c82eeb35e1c22d1))

### Features

- Automatically obtain cur_semester_id and biz_type_id and use them as default values
  ([`5b7c6e3`](https://github.com/Illustar0/ZZU.Py/commit/5b7c6e3bfffa0f98fcdbd5e3ed0774151ccd860e))

- Support obtain semester data
  ([`1c1e223`](https://github.com/Illustar0/ZZU.Py/commit/1c1e223ca1a71ea2c5cd24d39cb369579d6c2241))

- Support query of empty classrooms
  ([`f05ef9b`](https://github.com/Illustar0/ZZU.Py/commit/f05ef9b1c7e331e336f2eac4864a6cd40028d30d))

Allows to query empty classrooms by date and building id

Closes #9

### Refactoring

- Format code
  ([`daffc76`](https://github.com/Illustar0/ZZU.Py/commit/daffc764da425dbbf0ba4530b3b3266de173c44e))


## v4.0.0 (2025-03-08)

### Bug Fixes

- Allow specifying semester_id for get_courses()
  ([`faa0388`](https://github.com/Illustar0/ZZU.Py/commit/faa0388a663a676fa985b65c50e11d5418ff626d))

In fact, the semester_id is different for each semester, which means that get_courses() can only get
  the course schedule for the first semester of the 2024-2025 academic year. This commit fixes this
  problem.

BREAKING CHANGE: get_courses() required parameters changed

get_courses() now requires two parameters: start_date and semester_id

- Remove useless imports
  ([`d0fa47a`](https://github.com/Illustar0/ZZU.Py/commit/d0fa47a0874e00b4849328c844cc7d071e623337))

### Documentation

- Modify the comment format
  ([`0509e3f`](https://github.com/Illustar0/ZZU.Py/commit/0509e3f18722e2908fef11e9b3eea71a6761b7fe))

- Update README.md
  ([`71ced68`](https://github.com/Illustar0/ZZU.Py/commit/71ced688c89293c96e6ca1aaebcd50de4eb773ec))

### Features

- Allows obtaining userToken via public API
  ([`aff8a3c`](https://github.com/Illustar0/ZZU.Py/commit/aff8a3c93f2e4d4e7bd55c7c019b5c44a7f07b44))

- Make login() return a dictionary
  ([`5c6963c`](https://github.com/Illustar0/ZZU.Py/commit/5c6963ca2c4334effe9be513961b5cd0fbb29de9))

login() now returns a dictionary instead of a tuple

BREAKING CHANGE: login() return value changed

- Use pydantic to provide type annotations
  ([`e02d25c`](https://github.com/Illustar0/ZZU.Py/commit/e02d25c6f90e820e51a6be6cf746f84a69bfcf5f))


## v3.0.0 (2025-03-05)

### Bug Fixes

- Type hint error
  ([`86f2e23`](https://github.com/Illustar0/ZZU.Py/commit/86f2e2336ab45c41d78b6061753c05c06cb32829))

### Documentation

- Complete documentation for some internal functions
  ([`6552735`](https://github.com/Illustar0/ZZU.Py/commit/655273564b03b9d0bc8b3b89372d74b9f210fcdf))

- Correct and complete some documents
  ([`220f1da`](https://github.com/Illustar0/ZZU.Py/commit/220f1daacb9d4c3c559c3cc612fefa238428cd23))

### Features

- Introducing support for async io
  ([`87fb608`](https://github.com/Illustar0/ZZU.Py/commit/87fb6080df89bcef60eb2b66a274fcc868cd9f81))

- Use SimpleCookie as the incoming type
  ([`286be07`](https://github.com/Illustar0/ZZU.Py/commit/286be07343b08b671797bd3c9397616ad49b850f))

It is obvious that SimpleCookie is a more suitable parameter type than dict.

BREAKING CHANGE: no longer accepting dict type cookies

Please use SimpleCookie


## v2.1.0 (2025-03-03)

### Bug Fixes

- Forgot to delete the httpx top-level API
  ([`4a94ff5`](https://github.com/Illustar0/ZZU.Py/commit/4a94ff56b672b33eee2af6d651fe4a40e744afa7))

- Prevent program exit from being blocked
  ([`cdebda4`](https://github.com/Illustar0/ZZU.Py/commit/cdebda4d37d408e0fef808d8cd4b5dc31426b5b3))

- Wrong location_type in headers
  ([`30017fa`](https://github.com/Illustar0/ZZU.Py/commit/30017fa4e0a76f60dfbe0630dd7aa1a8b8507f55))

### Features

- Automatically refresh ecard_access_token
  ([`d7770d9`](https://github.com/Illustar0/ZZU.Py/commit/d7770d9715a3344e67193ba1396ebe608f4939c7))

- More detailed exceptions
  ([`da19688`](https://github.com/Illustar0/ZZU.Py/commit/da19688c8c4dec44aa10b4b22eebf4de9ae570ab))

- Perform permission check before operation
  ([`6378e4a`](https://github.com/Illustar0/ZZU.Py/commit/6378e4a2d9b9733b9b81e59715e6a66003f65031))

### Performance Improvements

- Reduce duplication of code
  ([`53b6844`](https://github.com/Illustar0/ZZU.Py/commit/53b68444fe8cc559d35c0dc2bae88fce6104a30e))

Reduce duplication of code and use some more elegant approach

- Remove unused functions
  ([`b07c0af`](https://github.com/Illustar0/ZZU.Py/commit/b07c0af4365e3754c547b73598c14e874bd4d92a))

Removed get_area_dict(), get_building_dict(), and get_unit_dict(), and integrated their
  functionality into get_room_dict()

DEPRECATED: all get_*_dict() except get_room_dict() are deprecated

The code for get_*_dict() is highly duplicated, so their functionality has been merged into
  get_room_dict(). From now on you should only use get_room_dict()

### Refactoring

- Format code
  ([`d70974f`](https://github.com/Illustar0/ZZU.Py/commit/d70974f223c736cfe9ef7360573428e974241062))


## v2.0.1 (2025-03-02)

### Bug Fixes

- Unable to generate document
  ([`b29393a`](https://github.com/Illustar0/ZZU.Py/commit/b29393ae56679d5975349e2da2b77a043c5b0805))


## v2.0.0 (2025-03-02)

### Chores

- Replace poetry with uv
  ([`e9da782`](https://github.com/Illustar0/ZZU.Py/commit/e9da782c4d57d4f7b02d5181f75ae2f49d996899))

uv is really too fast!

- Update build command
  ([`85ee7fc`](https://github.com/Illustar0/ZZU.Py/commit/85ee7fc67e670b894620a41eb65dfe3d93792712))

- Update renovate config
  ([`ec18baf`](https://github.com/Illustar0/ZZU.Py/commit/ec18baff35af8d44d05d7f7bee0a6720e2395642))

- Update version_toml
  ([`96c3a3f`](https://github.com/Illustar0/ZZU.Py/commit/96c3a3f8ac686c5817f0cd424c6363411b70098a))

- **deps**: Update python-semantic-release/publish-action action to v9.19.1
  ([#2](https://github.com/Illustar0/ZZU.Py/pull/2),
  [`6b98903`](https://github.com/Illustar0/ZZU.Py/commit/6b989035ae02b4385344c828ab071880a84ff66a))

Co-authored-by: renovate[bot] <29139614+renovate[bot]@users.noreply.github.com>

- **deps**: Update python-semantic-release/publish-action action to v9.20.0
  ([#5](https://github.com/Illustar0/ZZU.Py/pull/5),
  [`ed0a9f3`](https://github.com/Illustar0/ZZU.Py/commit/ed0a9f36edf0402bd0f234ef8010bec3ced41b8c))

Co-authored-by: renovate[bot] <29139614+renovate[bot]@users.noreply.github.com>

- **deps**: Update python-semantic-release/publish-action action to v9.21.0
  ([#7](https://github.com/Illustar0/ZZU.Py/pull/7),
  [`1364b87`](https://github.com/Illustar0/ZZU.Py/commit/1364b87966a21d49b650240e0a7156903061e91d))

Co-authored-by: renovate[bot] <29139614+renovate[bot]@users.noreply.github.com>

- **deps**: Update python-semantic-release/python-semantic-release action to v9.19.1
  ([#3](https://github.com/Illustar0/ZZU.Py/pull/3),
  [`3dd61a9`](https://github.com/Illustar0/ZZU.Py/commit/3dd61a94b56a5ace9ad73c7491bd8fb13e6eb424))

Co-authored-by: renovate[bot] <29139614+renovate[bot]@users.noreply.github.com>

- **deps**: Update python-semantic-release/python-semantic-release action to v9.20.0
  ([#6](https://github.com/Illustar0/ZZU.Py/pull/6),
  [`b8db4f7`](https://github.com/Illustar0/ZZU.Py/commit/b8db4f7096277f2c953428696c7dd39d839ccf09))

Co-authored-by: renovate[bot] <29139614+renovate[bot]@users.noreply.github.com>

- **deps**: Update python-semantic-release/python-semantic-release action to v9.21.0
  ([#8](https://github.com/Illustar0/ZZU.Py/pull/8),
  [`6d8550a`](https://github.com/Illustar0/ZZU.Py/commit/6d8550ab665a43d2560f7e4b522bb547c9a8f560))

Co-authored-by: renovate[bot] <29139614+renovate[bot]@users.noreply.github.com>

### Continuous Integration

- Fix the wrong command
  ([`25e764f`](https://github.com/Illustar0/ZZU.Py/commit/25e764f9aa89472789dfee124a210eb423cf7c7c))

- Modify commit message
  ([`0c49df9`](https://github.com/Illustar0/ZZU.Py/commit/0c49df983a0fb3eae037009ac8b6fdab74cfbff7))

### Features

- Allow cookie login
  ([`ebb159e`](https://github.com/Illustar0/ZZU.Py/commit/ebb159e7a193c9a8c64f1450024ef7750d38f36e))

Refactored the network processing module to allow logging in via cookies, as well as reformatted the
  code and added some logging

- Bump app version
  ([`16e9544`](https://github.com/Illustar0/ZZU.Py/commit/16e9544a3a4332b59480c4211a110ffdc64dafa0))

- Initial exception handling
  ([`94faba3`](https://github.com/Illustar0/ZZU.Py/commit/94faba31954e8a1fc27429c46efc06f8850f1748))

- Support for getting the default room
  ([`d0d7437`](https://github.com/Illustar0/ZZU.Py/commit/d0d74372b06cfaa5a2a5fe195853e4e8faf8d05c))

Now get_remaining_energy() and recharge_energy() can automatically get the default room of the
  account, so room is no longer a required parameter

BREAKING CHANGE: room parameter position adjustment

Since the room parameter is no longer necessary, the position of the room parameter of
  recharge_energy() has been adjusted

### Refactoring

- Format code
  ([`b3c81ad`](https://github.com/Illustar0/ZZU.Py/commit/b3c81ada9437e0d7e54fa8746019b5e579ff4fd5))

- Optimize imports
  ([`caceaa9`](https://github.com/Illustar0/ZZU.Py/commit/caceaa9172856143d3b865388a5c675298ff81e0))

### Breaking Changes

- Room parameter position adjustment


## v1.0.2 (2025-02-09)


## v1.0.1 (2025-02-09)

### Bug Fixes

- Fix a field error that caused the version to fail to be published
  ([`e7615ca`](https://github.com/Illustar0/ZZU.Py/commit/e7615caea2fc73b33096147000f250d8f1402be6))

Signed-off-by: Illustar0 <me@illustar0.com>

- License error
  ([`1f85a71`](https://github.com/Illustar0/ZZU.Py/commit/1f85a71df95363daa9017e967dc57836fc42a201))

Signed-off-by: Illustar0 <me@illustar0.com>

- Type error
  ([`a9c82f1`](https://github.com/Illustar0/ZZU.Py/commit/a9c82f15919e0249439d15d332b117d2062af0c1))

### Chores

- Change license
  ([`3186cbc`](https://github.com/Illustar0/ZZU.Py/commit/3186cbceeec150516989cc78874811afda6d6972))

Signed-off-by: Illustar0 <me@illustar0.com>


## v1.0.0 (2025-02-09)

### Bug Fixes

- Ci
  ([`6624b73`](https://github.com/Illustar0/ZZU.Py/commit/6624b73cfb873eb0320f4e1cb47836e74e87cbaf))

- Ci
  ([`332c003`](https://github.com/Illustar0/ZZU.Py/commit/332c003806e136bbe857f448c224485c6225c44f))

- Ci
  ([`be2466f`](https://github.com/Illustar0/ZZU.Py/commit/be2466fc025e060b2b65befdb2f5a7e6b433c407))

- Ci
  ([`603bef4`](https://github.com/Illustar0/ZZU.Py/commit/603bef4a2707f9baac5d29a8b3ecd7b431e50e0d))

- Dont work in python < 3.12
  ([`772feb3`](https://github.com/Illustar0/ZZU.Py/commit/772feb3bf340be0d3d96982adbc2092bb4e0ad64))

- Modify function name
  ([`1404ea1`](https://github.com/Illustar0/ZZU.Py/commit/1404ea1d94838edb096f55d1188938421745b21b))

- Portalauth
  ([`3760ff9`](https://github.com/Illustar0/ZZU.Py/commit/3760ff979130bce157b86c33333f11043f69e59f))

### Chores

- Add workflow
  ([`7dd6388`](https://github.com/Illustar0/ZZU.Py/commit/7dd638875c2da80c9aa70fa42541ea4ef278ff34))

- Bump code
  ([`abe655d`](https://github.com/Illustar0/ZZU.Py/commit/abe655defcd93fa9929484ec35bacc1e05745cc7))

- Bump dependencies
  ([`bc8ea0c`](https://github.com/Illustar0/ZZU.Py/commit/bc8ea0c46d6c6c8bd7c23807ab9c97e10ea5f709))

Signed-off-by: Illustar0 <me@illustar0.com>

- Bump version
  ([`16c224f`](https://github.com/Illustar0/ZZU.Py/commit/16c224f3e537a6e80d5ab8815d8b880e3bb7dd7d))

Signed-off-by: Illustar0 <me@illustar0.com>

- Bump version
  ([`4dbd8c3`](https://github.com/Illustar0/ZZU.Py/commit/4dbd8c33b8810eecff1cade275e2ce386a681f2d))

- Bump version
  ([`115ef22`](https://github.com/Illustar0/ZZU.Py/commit/115ef22c221cb2d703f0c38eafe3090f171370df))

- Bump version and years
  ([`2683ece`](https://github.com/Illustar0/ZZU.Py/commit/2683eceff8eabe328e033cbcbad39ebbcbf5b341))

- Bump years
  ([`a193e7e`](https://github.com/Illustar0/ZZU.Py/commit/a193e7eaa0641b73d740a31c4e2be1948dba704b))

- Edit LICENSE
  ([`02cba8e`](https://github.com/Illustar0/ZZU.Py/commit/02cba8e1bb32adcfb3781334c71ad1544ef2fb8c))

Signed-off-by: Illustar0 <me@illustar0.com>

- Fix docstring
  ([`94e16a4`](https://github.com/Illustar0/ZZU.Py/commit/94e16a47164b63aae13ba552bc1c2810e726b236))

- Modify characters
  ([`fe0b988`](https://github.com/Illustar0/ZZU.Py/commit/fe0b9887d99ef1cc594ae0baf7934a2fb4fe7f06))

- Update pyproject.toml
  ([`5ea1eaf`](https://github.com/Illustar0/ZZU.Py/commit/5ea1eaf5b8f2088621027946e0cc82f932c7a202))

### Code Style

- Fix code style
  ([`3c89771`](https://github.com/Illustar0/ZZU.Py/commit/3c897715522c5d42a2adac9db636c9f7239e9e6e))

- Format code
  ([`98f64c0`](https://github.com/Illustar0/ZZU.Py/commit/98f64c0327814e7b62bd95574edd218ef2ae0088))

### Continuous Integration

- Add release.yaml
  ([`b99340f`](https://github.com/Illustar0/ZZU.Py/commit/b99340fc74a3f4b4e632637d536649e252d4f8d8))

Signed-off-by: Illustar0 <me@illustar0.com>

- Rm unnecessary config
  ([`fd2ac02`](https://github.com/Illustar0/ZZU.Py/commit/fd2ac02cb8eadf9c3aff68a3738b16c32d69f9e4))

### Documentation

- Add class docstring
  ([`1368dca`](https://github.com/Illustar0/ZZU.Py/commit/1368dcad0c456ed09ad1b019d1d6d37c378e704b))

- Ci
  ([`ee9fcf4`](https://github.com/Illustar0/ZZU.Py/commit/ee9fcf484660bee9067e34fa54180c62390ab302))

- Edit network.py docstring
  ([`82484d4`](https://github.com/Illustar0/ZZU.Py/commit/82484d48fec5cc16f6fd3908305f37c9545b8613))

- Format
  ([`80b1b6d`](https://github.com/Illustar0/ZZU.Py/commit/80b1b6de323dfcb3c6353b86c292007a9dee60e8))

- Rm old docstring
  ([`04c7578`](https://github.com/Illustar0/ZZU.Py/commit/04c75782199a3b97d1678e76d2b57ad534a1f5ed))

- Update docs
  ([`d0e2537`](https://github.com/Illustar0/ZZU.Py/commit/d0e25376e05fe0a7547f6e5688a05799c1a5c69f))

- Update note
  ([`ec8e4de`](https://github.com/Illustar0/ZZU.Py/commit/ec8e4deb1d1791afe84573b64e75c7744b4e598f))

- Update note
  ([`7af9850`](https://github.com/Illustar0/ZZU.Py/commit/7af985071d2ebc445390ec5fb1e09e39d8034406))

- Update note
  ([`cac451c`](https://github.com/Illustar0/ZZU.Py/commit/cac451c9da54a1053c5a4ce3187044e10d088ba0))

- Update readme
  ([`25afc45`](https://github.com/Illustar0/ZZU.Py/commit/25afc45763396b81ac9f9826bf30177fec7674e9))

- Update readme
  ([`2209e60`](https://github.com/Illustar0/ZZU.Py/commit/2209e602ec6fd075cfb6e8c9ff966c2023831ac3))

### Features

- Add version
  ([`a6595ae`](https://github.com/Illustar0/ZZU.Py/commit/a6595ae406187863a96ed9e29774f42b42892aa3))

Signed-off-by: Illustar0 <me@illustar0.com>

- Bump app version
  ([`4d946ec`](https://github.com/Illustar0/ZZU.Py/commit/4d946ec4ea0260b59901535690fd910f56c06973))

Signed-off-by: Illustar0 <me@illustar0.com>

- Rewrite
  ([`ffcf67b`](https://github.com/Illustar0/ZZU.Py/commit/ffcf67b962e2cc024b0395c836a308c1b764f722))

- Support custom amt
  ([`a03596a`](https://github.com/Illustar0/ZZU.Py/commit/a03596aa7f1b9c8508196ceda3016e489d1934d4))

- Support isp cmcc
  ([`2cdba10`](https://github.com/Illustar0/ZZU.Py/commit/2cdba10aa3ad07ffc30506b3e05119a81d31797f))

- Support user self-service system
  ([`b1f9789`](https://github.com/Illustar0/ZZU.Py/commit/b1f97892a9e0ad385efb1c0b75fcdcba6445c33b))

### Refactoring

- Use ruff to replace black
  ([`734aab4`](https://github.com/Illustar0/ZZU.Py/commit/734aab4a15a8368d57f0f4e9542971bc29fa710d))

Signed-off-by: Illustar0 <me@illustar0.com>


## v0.1.0 (2024-10-20)

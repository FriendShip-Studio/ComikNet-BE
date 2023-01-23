# ComikNet - Backend API 文档

本文档旨在于指导你应如何与此后端服务器通信，以及取得数据的格式。

## 携带 Cookies 的请求

对于发往 `/login`, `/logout`, `/register`, `/favorite`, `/search`, `/history`, `/album`, `/chapter`, `/img_list`, `/img`, `/comment/comic`, `/comment/user`, `/comment`, `/tags` 的请求，后端会读取你所携带的 Cookies 来验证包括禁漫天堂登录状态与选定的镜像源。

- 对于后文所提到的`禁漫天堂Cookies包`，代指由禁漫天堂而来原文转发到用户终端上存储的一系列 Cookies，包含以下内容:
  - AVS
  - __cflb
  - ipcountry
  - ipm5

## 设置 Cookies 的请求

对于发往 `/captcha`, `/login`, `/logout`, `/favorite`, `/mirror` 的请求，后端会根据服务器的回应数据或处理结果，要求设置一些 Cookies 缓存数据。

## 用户信息

### /login

请求类型: POST

参数类型: JSON

| 数据键名 | 数据类型 | 是否必选  |
|:--------:|:--------:|:--------:|
| username |   str    |    ⭕    |
| password |   str    |    ⭕    |
| email    |   str    |    ⭕    |
| captcha  |   str    |    ⭕    |
| sex      |   str    |    ⭕    |

读取 Cookies: ✅，包含以下内容:

- 禁漫天堂Cookies包
- api_mirror

ComikNet-BE 将使用以上参数，尝试与禁漫天堂服务器后端通讯后，获得携带登录信息的 Cookies。

设置 Cookies: ✅，包含以下内容:

- 禁漫天堂Cookies包

返回数据类型: Json

| 数据键名  | 数据类型 |
|:---------:|:--------:|
|status_code|   int    |
|   data*   |   dict  |
| errorMsg* |   str   |

*: 如果没有顺利执行，`data` 将不会出现，转而是出现 `errorMsg`。

对于 `data`， 它的结构如下：

```json
{
    "uid" //用户的UID
    "username" //用户的用户名
    "email" //用户的邮箱
    "emailverified" //用户邮箱是否已验证
    "photo" //用户头像序列文件
    "fname" //暂不明确
    "gender" //性别，分别为 Male 或 Female
    "message" //欢迎信息，无作用
    "coin" //账户硬币
    "album_favorites" //账户内漫画收藏数
    "s" //暂不明确
    "favorite_list" //无作用
    "level_name" //目前佩戴的头衔
    "level" //用户等级
    "nextLevelExp" //距离升级所需经验值
    "exp" //当前经验值
    "expPercent" //已赚取经验值百分比
    "badges" //暂不明确
    "album_favorites_max" //目前账户可收藏数量上限
}
```

### /logout

请求类型: GET

无需参数

读取 Cookies: ✅，包含以下内容:

- 禁漫天堂Cookies包
- api_mirror

ComikNet-BE 将使用以上参数，尝试与禁漫天堂服务器后端通讯后，将此 Cookies 的账户登录状态设置为退出。

设置 Cookies: ✅，包含以下内容:

- 禁漫天堂Cookies包

返回数据类型: Json

| 数据键名  | 数据类型 |
|:---------:|:--------:|
|status_code|   int    |

### /captcha

请求类型: GET

无需参数

读取 Cookies: ❌

ComikNet-BE 将尝试开设一个注册会话并取得一个注册验证码图片。

设置 Cookies: ✅，包含以下内容:

- 禁漫天堂Cookies包

返回数据类型: Image/JPEG

### /register

**在运行 `/register/` 前，需要先运行 `/captcha` 来确保用户取得验证码以填写 `captcha` 字段。**

请求类型: POST

参数类型: JSON

| 数据键名 | 数据类型 | 是否必选  |
|:--------:|:--------:|:--------:|
| username |   str    |    ⭕    |
| password |   str    |    ⭕    |
| email    |   str    |    ⭕    |
| captcha  |   str    |    ⭕    |
| sex      |   str    |    ⭕    |

读取 Cookies: ✅，包含以下内容:

- 禁漫天堂Cookies包

ComikNet-BE 将使用以上参数，尝试与禁漫天堂服务器后端通讯后，请求一次账户注册。

设置 Cookies: ❌

返回数据类型: Json

| 数据键名  | 数据类型 |
|:---------:|:--------:|
|status_code|   int    |
|   data*   |   dict  |
| errorMsg* |   str   |

*: 如果没有顺利执行，`data` 将不会出现，转而是出现 `errorMsg`。

对于 `data`， 它将会是禁漫天堂后端对于此次注册请求的返回消息列表。这个列表将包含一个或数个字典，字典的 `type` 类型分为 `error` 和 `default`。对于前者，说明注册出现了问题。

无论注册是否成功，进一步的详细信息都将在字典的 `msg` 中给出。

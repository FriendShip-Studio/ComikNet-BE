# 部署和使用 ComikNet 指南

***作者:BiDuang***

***Friendship Studio (C) 2023***

## 前言

如果你正在阅读此指南，说明你已加入了 ComikNet Insider Preview 计划。我代表整个 ComikNet 向你的慷慨之举表达感谢！你在体验中所反馈的问题将帮助我们改进 ComikNet。

首先，ComikNet 是一个基于 Web 的漫画阅读站点。目前，它的数据来源是 `禁漫天堂` 的后端逆向工程而出的接口。因此，如果你平常有在使用 `禁漫天堂` 的话，那么你将发现 ComikNet 的基本上涵盖了禁漫天堂的操作，并提供了更多基于 `Friendship Cloud` 的功能。同时，由于去除了源站上的广告载入，ComikNet 的载入速度极快，并提供多源选择。*

当然，后续 ComikNet 将会变得更加强大：集成 `哔咔漫画` 的接口，并实现双源漫画同搜，极大提高用户的使用体验。

目前，ComikNet 具有以下功能：

- 禁漫天堂账户的登录和注册
- 漫画的搜索
- 漫画的详情页和阅读

未来，Friendship Cloud 上线后，还将与其联动集成：

- 基于 Friendship Cloud 的用户观看记录保存和标签分析
- 基于 Friendship Cloud 的用户推荐
- 基于 Friendship Cloud 的用户评论和群聊联动

**: 尚在开发中*  

加入 ComikNet Insider Preview，则说明你已同意[隐私协议](https://wiki.friendship.org.cn/wiki/FriendshipWiki:Privacy)。

## 部署

言归正传，我们将指导你如何部署并使用 ComikNet。

### 环境配置

最好使用 Windows 环境，因为这和作者的开发环境一致。下列教程都认为你使用的环境是安装了 Windows 10 及以上版本的计算机。  

#### NodeJs

前往[NodeJS官网](https://nodejs.org/zh-cn/download/)并选择 `长期维护版` 的安装包，下载并安装。

安装完成后，启动你计算机的命令行工具(按下 `Win` + `R` 并输入 `cmd` 后回车)，在里面输入以下命令：

```bash
nvm version
```

如果有版本号输出，说明安装成功。如果是一串报错指出此命令不存在，请尝试重启计算机或重新安装 NodeJs。

接下来，输入:

```bash
nvm list
```

如果列出的版本旁没有 `*`，请输入：(不要将方括号也输入进去)

```bash
nvm use [版本号]
```

如果有，则说明你已经安装好了 NodeJs。

#### Git

前往[Git官网](https://git-scm.com/download/)并下载安装包，安装即可。

对于除安装路径以外的其他选项，通常使用默认即可。

#### Python

**注意：务必要在开始安装时选择 Add to Path 选项，否则你将需要额外配置环境变量等参数**  
前往[Python官网](https://www.python.org/downloads/)并下载安装包，安装即可。

国内访问可能迟缓，可以前往本人的云盘下载3.11.0的安装包：<https://ero.114514.bid:1919/s/RJsN>

### 下载项目

ComikNet 分为三个部分:

- ComikNet-FE (前端，用于网页渲染)
- ComikNet-BE (后端，用于和源服务器通讯)
- ComikNet-Central (数据库端，用于处理 Friendship Cloud 数据)

如果你想把命令行工具的路径切换到某个路径，例如说D盘的AsakiRain文件夹，请输入:

```bash
cd /d D:/AsakiRain
```

请使用以下命令从 Friendship Studio 的公共仓库拉取最新提交，由于你刚刚把命令行的工作路径切换到了D盘的AsakiRain文件夹，因此数据将会出现在AsakiRain文件夹内。

依次输入：

```bash
git clone https://github.com/FriendShip-Studio/ComikNet-FE.git
git clone https://github.com/FriendShip-Studio/ComikNet-BE.git
git clone https://github.com/FriendShip-Studio/ComikNet-Central.git
```

国内访问 `Github` 可能有困难，可以改用此命令：

```bash
git clone https://kgithub.com/FriendShip-Studio/ComikNet-FE
git clone https://kgithub.com/FriendShip-Studio/ComikNet-BE.git
git clone https://kgithub.com/FriendShip-Studio/ComikNet-Central.git
```

### 初始化项目

#### ComikNet-FE

将你的命令行工作目录切换到此文件夹下，输入:

```bash
npm i
```

等待安装完成后，输入:

```bash
npm run dev
```

如果能正常启动并显示

```bash
  VITE v4.0.4  ready in 1919 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

说明前端已在 `http://localhost:5173/`准备好。

#### ComikNet-BE

将你的命令行工作目录切换到此文件夹下，输入:

```bash
pip install -r requirements.txt
```

然后，输入:

```bash
uvicorn main:app --reload
```

如果能正常启动并显示

```bash
INFO:     Will watch for changes in these directories: ['H:\\WorkSpace\\ComikNet\\WebView-Backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [38448] using WatchFiles
INFO:     Started server process [40040]
INFO:     Waiting for application start
```

说明后端已在 `http://localhost:8000/` 准备好。

#### ComikNet-Central

与 ComikNet-BE 配置方法一致，只需要更改此命令为：

```bash
uvicorn main:app --port 8080 --reload
```

即可。

全部开启完成后，你可以开始体验 ComikNet 了！

## 使用提示

建议你按照以下路径来体验：

- 如果没有账户，选择 `注册`
- 如果有账户，选择 `登录`
- 搜索一部漫画，悬停在搜索框上可以得到提示。
- 悬浮在漫画卡片上，可以获得漫画信息弹窗。点击漫画卡片，进入漫画详情页。
- 在漫画详情页进入源站点，然后点击原站点上的收藏按钮后返回 ComikNet 站点。
- 点击右上角的 `收藏夹`，可以看到你收藏的漫画。
- 点击右上角的 `观看历史`，可以看到你的历史记录。

祝你使用愉快！  

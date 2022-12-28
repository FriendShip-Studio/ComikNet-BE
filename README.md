# ComikNet-BE

基于 Python FastAPI 构建，为 ComikNet-FE 项目提供网络资源请求服务的后端。

此项目是 `Friendship Cloud` 的一部分。

(C) Friendship Studio, 2022

**警告：快速迭代的项目**

**此项目尚未推出稳定版本，因此尚不能在生产环境使用，且项目的结构或内容可能随时发生改动。**

## 主要功能

- 提供指定漫画站点的漫画搜索、阅读功能
- 提供漫画站点原生的用户基础功能
- 提供基于 Friendship Cloud 的用户分享、兴趣推荐。
- 在获得用户授权的情况下，提供基于漫画阅读记录的用户标签画像和历史总结

## 支持平台

|平台|状态|
|:-------:|:------------:|
| 禁漫天堂 |  🔨Working   |
| 哔咔漫画 |  📑Intend    |

## 运行方法

安装 `FastAPI`、`BeautifulSoup4` 和 `requests` 库。

```bash
pip install FastAPI BeautifulSoup4 requests
```
运行项目根目录下 `main.py` 文件。

```bash
uvicorn main:app --reload
```

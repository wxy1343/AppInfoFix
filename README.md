# Steam AppInfo 修复

## AppInfo 是什么

* 部分游戏`steam`账号没有游戏获取到的`AppInfo`不完整，导致`安装路径无效`和`应用配置无效`
* `AppInfo`保存了`steam`游戏的基础配置，包括安装的目录，游戏进程名称，清单信息
* `AppInfo`路径: `steam/appcache/appinfo.vdf`
* 判断`AppInfo`是否完整: 打开`steam://open/console`输入`app_info_print {appid}`查找`depots`和`config`是否存在

## 使用教程

1. 确保已入库游戏，`depotcache`存在清单，可以使用[一键入库工具](https://github.com/wxy1343/ManifestAutoUpdate/releases/tag/storage)入库游戏
2. 参数
    * `-a, --app-id`: 游戏id
    * `-i, --install-dir`: 安装目录
    * `-l, --launch`: 启动进程
    * `-d, --depot-id`: 仓库id
    * `-m, --manifest-gid`: 清单id
    * `-s, --size`: 仓库大小
3. 使用示例
    * 鬼谷八荒: `fix.exe -a 1468810 -i 鬼谷八荒 -l guigubahuang.exe -d 1468811 -m 6548132625584514585 -s 15503862689`
    * 中国式家长: `fix.exe -a 736190 -i 中国式家长 -l game.exe`
4. 注意事项
    * `-d, -m, -s`参数可以按需指定，如果不存在会优先从本地清单获取`清单id`和`大小`信息，如果`-d`
      参数不存在会从[清单仓库](https://github.com/wxy1343/ManifestAutoUpdate)获取信息
    * 修复完成后需要重启`steam`，重启后迅速点击下载游戏，不然`steam`会更新`appinfo`信息，需要重新修复
    * 下载完后如果无法运行报错`应用配置无效`还需要修复一遍

## 参考项目

* [leovp/steamfiles](https://github.com/leovp/steamfiles)
* [tralph3/Steam-Metadata-Editor](https://github.com/tralph3/Steam-Metadata-Editor)

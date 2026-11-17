# MySQL 8.0 Windows 10 图形化安装指南（拼音战机项目）

> 适用环境：Windows 10 64 位
> 目标：MySQL Server 8.0 + MySQL Workbench，端口 3306，root 密码认证，服务开机自启
> 说明：本指南由开发方提供，请在**你自己、具有管理员权限的 Windows 10 桌面**上按步骤操作。执行环境无管理员权限与图形界面，故安装由你本地完成。

---

## 一、下载安装包

1. 打开官网 Installer 下载页：https://dev.mysql.com/downloads/installer/
2. 下载 **`mysql-installer-community-8.0.xx.msi`**
   - 选文件体积**较大的完整离线版**（约 400+ MB），不要选 web 版，避免安装时反复联网下载失败
3. 页面若要求登录 / 注册 Oracle 账号，点下方 **"No thanks, just start my download."** 即可直接下载

## 二、安装向导（Installer）

1. 右键安装包 → **以管理员身份运行**（UAC 弹窗选"是"）
2. License Agreement：勾选 **"I accept the license terms"** → Next
3. Choosing a Setup Type：选 **Custom** → Next
   - 不要选 Developer Default，会装一堆本项目用不到的组件
4. Select Products（精确安装两样）：
   - 左侧树展开 **MySQL Servers → MySQL Server → MySQL Server 8.0**，选中 64 位版本 → 点 `>` 加入右侧
   - 展开 **Applications → MySQL Workbench → MySQL Workbench 8.0**，选中 → 点 `>` 加入右侧
   - 确认右侧恰好是这两项 → Next
5. Check Requirements：若有缺失依赖，点 **Execute** 令其自动安装 → Next
6. Installation：点 **Execute**，等待下载与安装（数分钟）→ Next

## 三、配置 MySQL Server（关键步骤）

1. Product Configuration → MySQL Server 8.0 → Next
2. **High Availability**：选 **Standalone MySQL Server / Classic MySQL Replication** → Next
3. **Type and Networking**：
   - Config Type：**Development Computer**（开发机，内存占用小）
   - 勾选 **TCP/IP**，端口填 **3306**
   - 可勾选 "Open Windows Firewall ports for network access"（按需）→ Next
4. **Authentication Method**：保持默认 **"Use Strong Password Encryption for Authentication (RECOMMENDED)"** → Next
   - 说明：后端将使用 `pymysql>=1.1.1`，支持 MySQL 8 默认的 `caching_sha2_password` 认证。若选 Legacy（`mysql_native_password`）也能用，但 MySQL 8.4 已移除该模式，建议保持默认。
5. **Accounts and Roles**：
   - 在 **MySQL Root Password** 与 **Repeat Password** 填入你自己设定的 root 密码，**务必记牢**
   - 暂不添加其他账号，先用 root → Next
6. **Windows Service**（对应"开机自启"验收项）：
   - 勾选 **"Configure MySQL Server as a Windows Service"**
   - Service Name 保持默认 **`MySQL80`**
   - 勾选 **"Start the MySQL Server at System Startup"**（开机自动启动）
   - Run Windows Service as：**Standard System Account** → Next
7. Server File Permissions：保持默认 → Next
8. 点 **Execute** 应用配置，等待各项出现绿色对勾 → **Finish**
9. 回到安装完成页 → **Finish** 关闭 Installer

## 四、验证安装（阶段 1 验收必做）

### 方法 A：命令行验证

打开 cmd（`Win + R` 输入 `cmd`），执行：

```cmd
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

输入密码后进入 `mysql>` 提示符，执行：

```sql
SELECT VERSION();
SHOW VARIABLES LIKE 'port';
SHOW VARIABLES LIKE 'default_authentication_plugin';
```

应看到版本 `8.0.x`、端口 `3306`、认证插件 `caching_sha2_password`。

### 方法 B：MySQL Workbench 连接（验收截图）

1. 开始菜单打开 **MySQL Workbench 8.0**
2. 首页 Connections 点 **Local Instance MySQL80**
3. 输入 root 密码，可勾选 "Save password in vault"（可选）
4. 成功进入主界面、左侧导航出现实例 → **截图保存**，即阶段 1 验收截图

### 方法 C：服务状态（验证开机自启）

- `Win + R` → `services.msc` → 找到 **MySQL80**
- 确认状态为"正在运行"、启动类型为"自动" → 可一并截图

## 五、常见坑

| 现象 | 解决办法 |
|---|---|
| 安装向导一闪退 | 必须"以管理员身份运行"；临时关闭杀毒软件重试 |
| 端口 3306 被占用 | cmd 执行 `netstat -ano \| findstr 3306` 找到 PID，任务管理器结束该进程 |
| Workbench 连不上 | 确认服务已启动（services.msc 看 MySQL80）；核对密码是否输对 |
| 命令行提示 mysql 不是内部命令 | 用上面的完整路径，或把 `C:\Program Files\MySQL\MySQL Server 8.0\bin` 加入 PATH |
| 认证插件相关报错 | 阶段 4 我会用兼容版 pymysql；若仍报错把原文发我 |

## 六、安全提示

> 你稍后提供的 root 密码，将**只写入项目本地配置文件（`.env`）**，并加入 `.gitignore`，**绝不会提交到已公开的 GitHub 仓库** `lijun618/pinyin-defense`。数据库账号仅用于本机开发联调。

## 七、完成阶段 1 后，请把以下信息发给我

1. MySQL 版本号（如 `8.0.36`）—— 来自 `SELECT VERSION();`
2. root 密码（用于建库建表、后端连接；仅写本地配置）
3. 端口是否 3306、MySQL80 服务是否已设为"自动"启动
4. Workbench 是否能正常连接（截图你自己留存即可，不必发我）

收到并确认无误后，我立即进入 **阶段 2**（创建 `pinyin_war_game` 数据库与数据表）。

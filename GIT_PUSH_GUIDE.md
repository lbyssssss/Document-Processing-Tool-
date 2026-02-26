# Git 推送说明

由于 GitHub HTTPS 推送需要用户名和密码/令牌，你需要在本地终端执行以下步骤：

## 方式一：使用个人访问令牌（推荐）

1. 生成 GitHub 访问令牌
   - 登录 GitHub
   - 点击右上角头像 -> Settings
   - 左侧菜单选择 "Developer settings"
   - 选择 "Personal access tokens"
   - 点击 "Generate new token"
   - 勾选 `repo` 权限
   - 复制生成的令牌

2. 在项目目录执行推送
   ```bash
   cd /workspace
   git push -u origin master
   ```
   - 当提示输入 Username 时，输入你的 GitHub 用户名
   - 当提示输入 Password 时，粘贴刚才生成的令牌
   - 密码可以留空

## 方式二：使用 SSH 密钥（如果已配置）

1. 生成 SSH 密钥（如果还没有）
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

2. 添加公钥到 GitHub
   - GitHub -> Settings -> SSH and GPG keys -> New SSH key
   - 复制公钥内容粘贴

3. 推送
   ```bash
   git remote set-url origin git@github.com:lbyssssss/Document-Processing-Tool-.git
   git push -u origin master
   ```

## 远程仓库信息

- 仓库地址：https://github.com/lbyssssss/Document-Processing-Tool-.git
- 当前分支：master
- 最近提交：9d1ac64 feat: add vite deps cache configuration

## 当前 Git 状态

```bash
git log --oneline -3
```

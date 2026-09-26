```markdown
# 🎮 Minecraft Manager Discord Bot

A modular, lightweight Discord bot designed to control an AWS-hosted Minecraft server managed via a Pterodactyl panel. It features interactive Discord UI components (buttons and dropdown menus) to monitor and manage both the AWS EC2 virtual machine and the Pterodactyl Minecraft container, backed by dynamic access controls.

---

## 🌟 Features

* **Interactive Control Panel:** One-click buttons to start/stop AWS EC2 instances and start/stop/restart the Minecraft server.
* **Status Inspection Dropdown:** Check AWS status, Minecraft status, or full system health directly within Discord.
* **Dynamic Permission Management:** Bot owner can grant or revoke server control permissions dynamically (`!allow` / `!deny`).
* **Environment Variable Protection:** Keeps all private keys, API credentials, and server IDs isolated in a `.env` file.

---

## 🛠️ Prerequisites

Before installing, make sure you have:

* **Python 3.8+** installed.
* A **Discord Bot Token** with `Message Content Intent` enabled from the [Discord Developer Portal](https://discord.com/developers/applications).
* An **AWS IAM User** access key with permissions to start/stop the target EC2 instance.
* A **Pterodactyl Client API Key** (`ptlc_...`) generated under your Pterodactyl account settings.

---

## 🚀 Quick Setup & Installation

### 1. Clone the Repository

```bash
git clone [https://github.com/masupremeho/minecraft-manager-bot.git](https://github.com/masupremeho/minecraft-manager-bot.git)
cd minecraft-manager-bot

```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

```

### 3. Environment Configuration

Copy `.env.example` to create your local `.env` configuration file:

```bash
cp .env.example .env

```

Open `.env` in a text editor and fill in your details:

```env
DISCORD_TOKEN=your_discord_bot_token_here
BOT_OWNER_ID=your_discord_user_id_here

AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=eu-central-1
EC2_INSTANCE_ID=i-0123456789abcdef0

PTERO_URL=[http://your-panel-domain.com](http://your-panel-domain.com)
PTERO_API_KEY=ptlc_your_client_api_key_here
PTERO_SERVER_ID=your_8_char_server_id

SERVER_ADDRESS=your.server.domain.com

```

---

## ⚙️ Environment Variables Reference

| Variable | Description |
| --- | --- |
| `DISCORD_TOKEN` | Bot application token from Discord Developer Portal. |
| `BOT_OWNER_ID` | Numeric Discord User ID of the primary owner (permanent admin). |
| `AWS_ACCESS_KEY_ID` | AWS IAM Access Key ID. |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM Secret Access Key. |
| `AWS_REGION` | AWS Region hosting your EC2 instance (e.g., `eu-central-1`). |
| `EC2_INSTANCE_ID` | Target AWS EC2 Instance ID (e.g., `i-0123456789abcdef0`). |
| `PTERO_URL` | Base URL of your Pterodactyl Panel. |
| `PTERO_API_KEY` | Pterodactyl Client API Key. |
| `PTERO_SERVER_ID` | Short 8-character server ID from your server URL. |
| `SERVER_ADDRESS` | Display address shown on the Discord activity and panel embed. |

---

## 🏃 Running the Bot

Run the main script locally or on your hosting provider:

```bash
python Main.py

```

### Deployment (e.g., Datalix / Pterodactyl Bot Hosting)

1. Clone this repository directly into your hosting panel file manager.
2. Create a `.env` file containing your secret credentials.
3. Set your startup command to run `Main.py` (or `python3 Main.py`).

---

## 📖 Commands Reference

| Command | Syntax | Description | Permission Level |
| --- | --- | --- | --- |
| `!panel` | `!panel` | Sends the control panel embed with interactive buttons and dropdown status menu. | Permitted Users |
| `!allow` | `!allow @User` | Adds a user to the allowed list for server control. | Owner Only |
| `!deny` | `!deny @User` | Removes a user from the allowed list. | Owner Only |
| `!listusers` | `!listusers` | Displays all users currently permitted to control the server. | Owner Only |

---

## 🛡️ Security Note

Never commit `.env` or `allowed_users.json` to a public repository. Ensure `.gitignore` remains configured to ignore runtime credentials.

```

---

### How to Add This to Your GitHub Repository

1. Copy the code block above using the **Copy** button in the top right of the box.
2. Open your repository on GitHub: [https://github.com/masupremeho/minecraft-manager-bot](https://github.com/masupremeho/minecraft-manager-bot)
3. Click the **Add file** button near the top right and select **Create new file**.
4. Type `README.md` into the file name box.
5. Paste the copied text directly into the main text box.
6. Click the green **Commit changes...** button at the top right, then click **Commit changes** again in the popup.

<FollowUp>Did you manage to paste and commit the README on GitHub?</FollowUp>

<ElicitationsGroup>
  <Elicitations message="What would you like to do next?">
    <Elicitation label="Deploy to Datalix" query="The README is added! How do I clone and configure this on Datalix now?"/>
    <Elicitation label="Test Bot Locally" query="How do I run Main.py locally to test the commands before hosting?"/>
  </Elicitations>
</ElicitationsGroup>

```

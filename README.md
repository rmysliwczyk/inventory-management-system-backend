# Inventory Management System API
API for keeping track of inventory assets. Check out the frontend [here](github.com/rmysliwczyk/inventory-management-system-frontend)
## 🌟 Highlights 
- 🌐 REST architecture
- 🔐 Secure JWT Tokens Authentication with password hashing
- 🛂💉 Authorization via endpoint controllers role dependency injection
- 🧪 Automated testing with Pytest and GitHub Actions
- ✨ Clean and simple
- 🔁 Database migrations

## 💻 Technologies used
- <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/refs/heads/main/icons/Python-Light.svg" width=24/> **Python** for the programming language
- <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/refs/heads/main/icons/FastAPI.svg" width=24/> **FastAPI** for the API framework
- <img src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/swagger.svg" width=24/> **Swagger** for the interactive API docs
- <img src="https://raw.githubusercontent.com/fastapi/sqlmodel/refs/heads/main/docs/img/icon.svg" width=24/> **SQLModel** for the ORM and database integration
- <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/refs/heads/main/icons/SQLite.svg" width=24/> **SQLite** for the database
- <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/refs/heads/main/icons/Jenkins-Light.svg" width=24/> **Jenkins** for automatic deployment (CI/CD)
- <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/refs/heads/main/icons/Docker.svg" width=24/> **Docker** for CI/CD
- <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/refs/heads/main/icons/GithubActions-Light.svg" width=24/> **GitHub Actions** for automatic integration/unit tests with pytest (CI/CD)

## 👉 Try it!
Self hosted here: [ims-api.mysliwczykrafal.pl/docs](https://ims-api.mysliwczykrafal.pl/docs)  
|Account type|Login|Password|
|------------|-----|--------|
|Admin       |admin| admin  |
|Regular user|user |user    |

## 📥 Deployment
If you wish to deploy the app yourself follow these steps:
* Install [Docker](https://docs.docker.com/engine/install/) or [Podman](https://podman.io/docs/installation). If you use Podman, replace `docker` command with `podman` in the following steps.
* `git clone` the repository or download and extract the .zip with the source code.
* `cd /directory/with/the/sourcecode`
* `mv .env.example .env`
* For security, make sure to edit the default variables values in .env
* `docker build -t "ims-backend" .`
* `docker run -d --rm --name "ims-backend" -p 8004:8004 "ims-backend"`
* Visit `http://127.0.0.1/docs` to check if the API is running

## 📝 Project details
Description of work organization and demo deployment details  

No AI was used for the code of documentation of this project. I'm not opposed to using AI tools in the right context, but for the purpose of my personal portfolio projects I've decided not to use them.

### Tools and resources
#### Project management
- <img src="https://raw.githubusercontent.com/LelouchFR/skill-icons/refs/heads/main/assets/git-auto.svg" width=24/> **Git** for version control
- <img src="https://raw.githubusercontent.com/LelouchFR/skill-icons/refs/heads/main/assets/uml-auto.svg" width=24/> **UML** for Use case, Activity, and Class diagrams
- <img src="https://raw.githubusercontent.com/LelouchFR/skill-icons/refs/heads/main/assets/jira-auto.svg" width=24/> **Jira** for tracking tasks and bugs

#### Deployment
- <img src="https://raw.githubusercontent.com/LelouchFR/skill-icons/refs/heads/main/assets/linux-auto.svg" width=24/> Local homelab server running **Debian Linux**
- 🌎 **Dynamic DNS** with [Dynu](https://www.dynu.com) for hosting with dynamic IP
- <img src="https://github.com/LelouchFR/skill-icons/blob/main/assets/nginx.svg" width=24/> **NGINX** for reverse proxy
- <img src="https://raw.githubusercontent.com/LelouchFR/skill-icons/refs/heads/main/assets/github-auto.svg" width=24/> **GitHub webhook** for triggering Jenkins build and deployment
- 🌐 **HTTPS** with certbot and Let's Encrypt

### Diagrams
#### Database diagram (ERD)
<img src="diagrams/Inventory Management System - ERD.png" width=512/>  

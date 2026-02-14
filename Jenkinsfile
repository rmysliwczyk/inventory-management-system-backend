pipeline {
    agent any

    stages {
        stage('Prepare Environment') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'DATABASE_SYSTEM', variable: 'DATABASE_SYSTEM'),
                        string(credentialsId: 'DATABASE_FILENAME', variable: 'DATABASE_FILENAME'),
                        string(credentialsId: 'ADMIN_USERNAME', variable: 'ADMIN_USERNAME'),
                        string(credentialsId: 'ADMIN_PASSWORD', variable: 'ADMIN_PASSWORD'),
                        string(credentialsId: 'USER_USERNAME', variable: 'USER_USERNAME'),
                        string(credentialsId: 'USER_PASSWORD', variable: 'USER_PASSWORD'),
                        string(credentialsId: 'SECRET_KEY', variable: 'SECRET_KEY'),
                        string(credentialsId: 'ALGORITHM', variable: 'ALGORITHM'),
                        string(credentialsId: 'ACCESS_TOKEN_EXPIRE', variable: 'ACCESS_TOKEN_EXPIRE')
                    ]) {
                        sh """
                        rm .env || true
                        echo "DATABASE_SYSTEM=${DATABASE_SYSTEM}" >> .env
                        echo "DATABASE_FILENAME=${DATABASE_FILENAME}" >> .env
                        echo "ADMIN_USERNAME=${ADMIN_USERNAME}" >> .env
                        echo "ADMIN_PASSWORD=${ADMIN_PASSWORD}" >> .env
                        echo "USER_USERNAME=${USER_USERNAME}" >> .env
                        echo "USER_PASSWORD=${USER_PASSWORD}" >> .env
                        echo "SECRET_KEY=${SECRET_KEY}" >> .env
                        echo "ALGORITHM=${ALGORITHM}" >> .env
                        echo "ACCESS_TOKEN_EXPIRE=${ACCESS_TOKEN_EXPIRE}" >> .env
                        """
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t \"ims-backend\" .'
            }
        }

        stage('Stop and Remove Existing Container') {
            steps {
                sh 'docker stop ims-backend || true'
                sh 'docker rm ims-backend || true'
            }
        }

        stage('Run New Container') {
            steps {
                sh 'docker run -v database:/app/database -d --restart always --name \"ims-backend\" -p 8004:8004 \"ims-backend\"'
            }
        }
    }
}

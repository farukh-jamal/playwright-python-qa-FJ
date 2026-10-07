pipeline {
    agent any

    stages {
        stage('Verify Environment') {
            steps {
                bat 'python --version'
                bat 'git --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }
    }
}
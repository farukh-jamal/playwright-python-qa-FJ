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

        stage('Install Playwright Browser') {
            steps {
                bat 'python -m playwright install chromium'
            }
        }
        stage('Run Automated Tests') {
    steps {
        bat 'python -m pytest'
    }
     
}
}
post {
    always {
        junit 'reports/junit.xml'
    }
}
}
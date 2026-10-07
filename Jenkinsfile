pipeline {
    agent any

    stages {
        stage('Verify Environment') {
            steps {
                bat 'python --version'
                bat 'git --version'
            }
        }
    }
}
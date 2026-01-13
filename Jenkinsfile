pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Create Virtual Environment') {
            steps {
                bat '''
                if exist %VENV_DIR% (
                    rmdir /s /q %VENV_DIR%
                )
                python -m venv %VENV_DIR%
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                call %VENV_DIR%\\Scripts\\activate
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Python Scripts') {
            steps {
                bat '''
                call %VENV_DIR%\\Scripts\\activate
                for %%f in (scripts\\*.py) do (
                    echo ---------------------------------
                    echo Running %%f
                    python %%f
                    if ERRORLEVEL 1 (
                        echo Script %%f failed
                        exit /b 1
                    )
                )
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully'
        }
        failure {
            echo '❌ Pipeline failed'
        }
    }
}

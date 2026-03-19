pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Setup Python') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Extract Sources') {
      steps {
        sh '''
          . .venv/bin/activate
          python src/extract/docling_extract.py
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'extracted/*.json', fingerprint: true
    }
  }
}

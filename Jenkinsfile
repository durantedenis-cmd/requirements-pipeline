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
        bat '''
          python -m venv .venv
          call .venv\\Scripts\\activate
          python -m pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Extract Sources') {
      steps {
        bat '''
          call .venv\\Scripts\\activate
          python src\\extract\\docling_extract.py
        '''
      }
    }
    stage('Build Canonical Model') {
      steps {
        bat '''
          call .venv\\Scripts\\activate
          python src\\normalize\\build_canonical_model.py
        '''
      }
    }
    stage('Detect Deltas') {
      steps {
      bat '''
        call .venv\\Scripts\\activate
        python src\\normalize\\detect_deltas.py
      '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'extracted/*.json, canonical/*.json', fingerprint: true
    }
  }
}

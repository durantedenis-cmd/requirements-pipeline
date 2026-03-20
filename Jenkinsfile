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
    stage('Generate Backlog Items') {
      environment {
      OPENAI_API_KEY = credentials('openai-api-key')
    }
      steps {
      bat '''
        call .venv\\Scripts\\activate
        python src\\derive\\generate_backlog_items.py
      '''
      }
    }
    stage('Generate Test Design') {
      environment {
      OPENAI_API_KEY = credentials('openai-api-key')
    }
      steps {
      bat '''
        call .venv\\Scripts\\activate
        python src\\derive\\generate_test_design.py
      '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'extracted/*.json, canonical/*.json, derived/*.json', fingerprint: true
    }
  }
}

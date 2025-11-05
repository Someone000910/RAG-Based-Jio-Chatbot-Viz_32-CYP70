// Jenkinsfile (Corrected for Docker Shell)
pipeline {
    // Uses a Docker agent for a clean, consistent Python 3.10 environment.
    agent {
        docker {
            image 'python:3.10-slim'
            args '-u root'
        }
    }

    // Environment variables
    environment {
        // --- Deployment Variables (REPLACED with your values) ---
        EC2_PUBLIC_IP = '3.110.136.56'
        EC2_HOST = "ubuntu@3.110.136.56" 
        REMOTE_APP_PATH = '/home/ubuntu/jio-rag-chatbot'
        SSH_CREDENTIAL_ID = 'aws-deploy-key' 
        
        // --- Application Variables (Set as Jenkins Secrets) ---
        GOOGLE_API_KEY_SECRET_ID = 'google-api-key-secret' 
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Cloning the GitHub repository...'
                git branch: 'main', url: 'https://github.com/Someone000910/RAG-Based-Jio-Chatbot-Viz_32-CYP70.git'
            }
        }

        stage('Setup Environment & Dependencies') {
            steps {
                echo 'Installing Python dependencies on Jenkins Agent...'
                sh 'python -m venv venv'
                // FIX: Replaced 'source' with '.' for POSIX compliance in the Docker shell
                sh '. venv/bin/activate' 
                sh 'pip install --no-cache-dir -r requirements.txt'
            }
        }

        stage('Run Data Pipeline') {
            steps {
                // Inject the GOOGLE_API_KEY securely from Jenkins credentials
                withCredentials([string(credentialsId: env.GOOGLE_API_KEY_SECRET_ID, variable: 'GOOGLE_API_KEY_VALUE')]) {
                    echo 'Running RAG Data Pipeline Steps...'
                    
                    // Set environment variable for the RAG scripts
                    sh 'export GOOGLE_API_KEY=$GOOGLE_API_KEY_VALUE'
                    
                    // FIX: Replaced 'source' with '.' for POSIX compliance
                    sh '. venv/bin/activate' 
                    
                    // --- Build & Process Knowledge Base Steps (Using python3 for consistency) ---
                    sh 'cd extraction && python3 build_knowledge_base.py'
                    sh 'cd extraction && python3 clean_json_data.py -i data/knowledge_base.json -o data/knowledge_base_cleaned.json'
                    sh 'cd chunking && python3 run_all_chunkers.py'
                    
                    // --- Generate Embeddings (Memory intensive step) ---
                    sh 'cd embedding && python3 generate_minilm_embeddings.py'
                    sh 'cd embedding && python3 generate_bge_embeddings.py'
                    sh 'cd embedding && python3 generate_e5_embeddings.py'
                    
                    echo 'Data Pipeline Complete. FAISS files generated in workspace.'
                }
            }
        }

        stage('Deploy to AWS EC2') {
            steps {
                echo "Initiating deployment to AWS EC2 at ${env.EC2_HOST}..."
                
                // Use Jenkins SSH Agent plugin for secure access
                sshagent(credentials: [env.SSH_CREDENTIAL_ID]) {
                    // Create remote directory
                    sh "ssh -o StrictHostKeyChecking=no ${env.EC2_HOST} 'mkdir -p ${env.REMOTE_APP_PATH}'"
                    
                    // Copy code and all generated data files (including *.faiss)
                    sh "rsync -avz --exclude 'venv' --exclude 'node_modules' --exclude '.git' ./ ${env.EC2_HOST}:${env.REMOTE_APP_PATH}"

                    // Execute remote commands on the EC2 instance
                    sh """
                        ssh ${env.EC2_HOST} << EOF
                        cd ${env.REMOTE_APP_PATH}
                        
                        echo 'Setting up environment on EC2...'
                        python3 -m venv venv_deploy
                        source venv_deploy/bin/activate
                        pip install --no-cache-dir -r requirements.txt
                        
                        echo 'Creating .env file with API Key...'
                        # Note: \$GOOGLE_API_KEY_VALUE is retrieved securely by Jenkins
                        echo "GOOGLE_API_KEY=\\"\$GOOGLE_API_KEY_VALUE\\"" > .env
                        
                        echo 'Starting Streamlit app with PM2...'
                        pm2 stop jio-chatbot || true
                        pm2 delete jio-chatbot || true 
                        
                        # Use the streamlit binary from the newly created venv_deploy
                        pm2 start ./venv_deploy/bin/streamlit --name jio-chatbot -- run app.py --server.port 8501
                        pm2 save # Save the process list
                        
                        EOF
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo "✅ Deployment successful! Chatbot should be live on http://${env.EC2_PUBLIC_IP}:8501"
        }
        failure {
            echo '❌ Pipeline failed! Review the console output for Python or dependency errors.'
        }
    }
}

pipeline {
    // We'll use a Docker agent for consistency, ensuring Python and necessary tools are present.
    // If you don't have Docker set up on your Jenkins agent, change this to 'agent any'
    // and ensure Python 3.8+ is installed on the agent.
    agent {
        docker {
            image 'python:3.10-slim' // Or an image with Python 3.8 or higher
            args '-u root' // Needed if permissions are an issue with volume mounts
        }
    }

    // Environment variables
    environment {
        // --- Jenkins-Specific Variables ---
        // Name of the Python tool configuration if using 'agent any'
        PYTHON_TOOL_NAME = 'python310' // **REPLACE IF USING AGENT ANY**

        // --- Deployment Variables ---
        EC2_HOST = 'ubuntu@your-target-ec2-ip.compute-1.amazonaws.com' // **REPLACE THIS**
        REMOTE_APP_PATH = '/home/ubuntu/jio-rag-chatbot'
        SSH_CREDENTIAL_ID = 'aws-deploy-key' // **REPLACE THIS**

        // --- Application Variables (Set as Jenkins Secrets for security) ---
        // This MUST be set as a Secret Text credential in Jenkins!
        GOOGLE_API_KEY_SECRET_ID = 'google-api-key-secret' // **REPLACE THIS**
    }

    // --- Credentials setup for the GOOGLE_API_KEY ---
    // The actual GOOGLE_API_KEY value will be injected into the build environment
    // as an environment variable named GOOGLE_API_KEY
    tools {
        // If using 'agent any', specify the python version here:
        // python env.PYTHON_TOOL_NAME
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Cloning the GitHub repository...'
                // Use the correct repository URL and branch
                git branch: 'main', url: 'https://github.com/Someone000910/RAG-Based-Jio-Chatbot-Viz_32-CYP70.git'
            }
        }

        stage('Setup Environment & Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh 'python -m venv venv'
                sh 'source venv/bin/activate'
                sh 'pip install --no-cache-dir -r requirements.txt'
            }
        }

        stage('Run Data Pipeline') {
            steps {
                // Inject the GOOGLE_API_KEY securely from Jenkins credentials
                withCredentials([string(credentialsId: env.GOOGLE_API_KEY_SECRET_ID, variable: 'GOOGLE_API_KEY_VALUE')]) {
                    echo 'Running RAG Data Pipeline Steps...'
                    // 1. Set environment variable for the scripts
                    sh 'export GOOGLE_API_KEY=$GOOGLE_API_KEY_VALUE'
                    
                    // --- Step 2: Build Knowledge Base (Step 1 assumed manual/pre-done) ---
                    sh 'cd extraction && python build_knowledge_base.py'

                    // --- Step 3: Clean Data ---
                    sh 'cd extraction && python clean_json_data.py -i data/knowledge_base.json -o data/knowledge_base_cleaned.json'
                    
                    // --- Step 4: Generate Chunks ---
                    sh 'cd chunking && python run_all_chunkers.py'
                    
                    // --- Step 5: Generate Embeddings (Crucial, must be run sequentially) ---
                    // Note: This step is memory intensive! Ensure your Jenkins agent has enough RAM.
                    sh 'cd embedding && python generate_minilm_embeddings.py'
                    sh 'cd embedding && python generate_bge_embeddings.py'
                    sh 'cd embedding && python generate_e5_embeddings.py'
                    
                    echo 'Data Pipeline Complete. FAISS files generated in workspace.'
                }
            }
        }

        stage('Deploy to AWS EC2') {
            steps {
                echo 'Initiating deployment to AWS EC2...'
                
                // Use Jenkins SSH Agent plugin for secure access
                sshagent(credentials: [env.SSH_CREDENTIAL_ID]) {
                    // Create remote directory and necessary files (like .env)
                    sh "ssh -o StrictHostKeyChecking=no ${env.EC2_HOST} 'mkdir -p ${env.REMOTE_APP_PATH}'"
                    
                    // Copy all generated files (including the large *.faiss index files)
                    sh "rsync -avz --exclude 'venv' --exclude 'node_modules' --exclude '.git' ./ ${env.EC2_HOST}:${env.REMOTE_APP_PATH}"

                    // Execute remote commands on the EC2 instance
                    sh """
                        ssh ${env.EC2_HOST} << EOF
                        cd ${env.REMOTE_APP_PATH}
                        
                        echo 'Setting up environment on EC2...'
                        # Create virtual environment and install dependencies on the target server
                        python3 -m venv venv_deploy
                        source venv_deploy/bin/activate
                        pip install --no-cache-dir -r requirements.txt
                        
                        echo 'Creating .env file with API Key...'
                        # Create the .env file with the API Key for the Streamlit app
                        # This assumes you have a safe way to pass the key; using Jenkins Secrets is best.
                        echo "GOOGLE_API_KEY=\\"\$GOOGLE_API_KEY_VALUE\\"" > .env
                        
                        echo 'Starting Streamlit app with PM2...'
                        # Use PM2 to manage the Streamlit application in the background
                        pm2 stop jio-chatbot || true
                        pm2 delete jio-chatbot || true 
                        
                        # PM2 command to run the Streamlit app
                        # Ensure the 'streamlit' command is available in the venv_deploy path
                        # If using the venv_deploy, the path is: ./venv_deploy/bin/streamlit
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
            echo '✅ Deployment successful! Chatbot should be live on port 8501.'
        }
        failure {
            echo '❌ Pipeline failed! Review the console output for Python or dependency errors.'
        }
    }
}

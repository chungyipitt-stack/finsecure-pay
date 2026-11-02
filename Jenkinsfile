// =============================================================================
// FinSecure Pay - CI/CD pipeline
// Checkout -> Build -> Unit Test -> Code Quality (SonarCloud) -> Dependency Scan
// (OWASP) -> Package -> Container Build -> Image Scan (Trivy) -> Push (Docker Hub)
// -> Deploy (EKS) -> Smoke Test.   Optional: ROLLBACK mode.
//
// Required Jenkins credentials (Manage Jenkins > Credentials) - none live in Git:
//   dockerhub-creds    Username/Password  Docker Hub user + access token
//   sonarcloud-token   Secret text        SonarCloud user token
//   nvd-api-key        Secret text        NVD API key for OWASP Dependency-Check
//   aws-creds          Username/Password  AWS access key id / secret access key
//   finsecure-api-key  Secret text        API key injected into the K8s Secret
// =============================================================================
pipeline {
    agent any

    parameters {
        choice(name: 'MODE', choices: ['deploy', 'rollback'],
               description: 'deploy = full CI/CD; rollback = revert EKS to a previous image/revision')
        string(name: 'ROLLBACK_TAG', defaultValue: '',
               description: 'rollback mode: image tag to roll back to (empty = previous revision via kubectl rollout undo)')
        booleanParam(name: 'SKIP_SONAR', defaultValue: false, description: 'Skip SonarCloud analysis (e.g. offline)')
        booleanParam(name: 'SIMULATE_TEST_FAILURE', defaultValue: false,
                     description: 'TC02: Introduce a controlled failing unit test to verify deployment is blocked')
        booleanParam(name: 'SIMULATE_SECURITY_FINDING', defaultValue: false,
                     description: 'TC07: Introduce a controlled CRITICAL security finding (CVE-2022-42889) to verify the security gate blocks release')
    }

    triggers {
        // Poll GitHub every 2 minutes (works behind NAT). Replace with githubPush() if a webhook/ngrok is used.
        pollSCM('H/2 * * * *')
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 60, unit: 'MINUTES')
    }

    environment {
        APP_NAME        = 'finsecure-pay'
        DOCKERHUB_USER  = 'chungyi1979'
        IMAGE_REPO      = "${DOCKERHUB_USER}/${APP_NAME}"
        AWS_REGION      = 'ap-southeast-1'
        EKS_CLUSTER     = 'finsecure-eks'
        K8S_NAMESPACE   = 'finsecure'
        SONAR_ORG       = 'chungyipitt-stack'
        SONAR_PROJECT   = 'chungyipitt-stack_finsecure-pay'
        NOTIFY_EMAIL    = 'chungyi.pitt@gmail.com'
        DC_DATA_DIR     = '/var/jenkins_home/dependency-check-data'   // cached NVD database
        TRIVY_CACHE_DIR = '/var/jenkins_home/trivy-cache'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'chmod +x mvnw && git log -1 --pretty="Commit %h by %an: %s"'
                script {
                    env.RUN_MODE = params.MODE ?: 'deploy'
                    env.GIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.POM_VERSION = sh(script: "./mvnw -q help:evaluate -Dexpression=project.version -DforceStdout",
                                         returnStdout: true).trim()
                    // Meaningful, traceable version: <semver>-<build>-<commit>
                    env.IMAGE_TAG = "${env.POM_VERSION}-${env.BUILD_NUMBER}-${env.GIT_SHORT}"
                    currentBuild.displayName = "#${env.BUILD_NUMBER} ${env.RUN_MODE} ${env.RUN_MODE == 'deploy' ? env.IMAGE_TAG : (params.ROLLBACK_TAG ?: 'prev')}"
                }
            }
        }

        // ------------------------------------------------------------- CI ----
        stage('Build') {
            when { expression { env.RUN_MODE == 'deploy' } }
            steps { sh './mvnw -B -ntp clean compile' }
        }

        stage('Unit Test') {
            when { expression { env.RUN_MODE == 'deploy' } }
            steps {
                // A failing test fails this stage, and therefore the whole pipeline - nothing is deployed.
                script {
                    def failFlag = (params.SIMULATE_TEST_FAILURE == true) ? '-Dfinsecure.test.simulateFailure=true' : ''
                    sh "./mvnw -B -ntp test ${failFlag}"
                }
            }
            post {
                always {
                    junit testResults: 'target/surefire-reports/*.xml', allowEmptyResults: false
                    archiveArtifacts artifacts: 'target/site/jacoco/**', allowEmptyArchive: true
                }
            }
        }

        stage('Code Quality - SonarCloud') {
            when { allOf { expression { env.RUN_MODE == 'deploy' }; expression { !params.SKIP_SONAR } } }
            steps {
                retry(2) {
                    withCredentials([string(credentialsId: 'sonarcloud-token', variable: 'SONAR_TOKEN')]) {
                        // sonar.qualitygate.wait=true makes the scanner fail the build if the Quality Gate fails
                        sh '''
                          ./mvnw -B -ntp org.sonarsource.scanner.maven:sonar-maven-plugin:5.8.0.7211:sonar \
                            -Dsonar.organization=${SONAR_ORG} \
                            -Dsonar.projectKey=${SONAR_PROJECT} \
                            -Dsonar.token=${SONAR_TOKEN} \
                            -Dsonar.ws.timeout=180 \
                            -Dsonar.qualitygate.wait=true \
                            -Dsonar.qualitygate.timeout=300
                        '''
                    }
                }
            }
        }

        stage('Dependency Scan - OWASP') {
            when { expression { env.RUN_MODE == 'deploy' } }
            steps {
                withCredentials([string(credentialsId: 'nvd-api-key', variable: 'NVD_API_KEY')]) {
                    // SECURITY GATE #1: fails when any dependency has a CVE with CVSS >= 7 (HIGH/CRITICAL)
                    script {
                        def secProfile = (params.SIMULATE_SECURITY_FINDING == true) ? '-Psimulate-security-finding' : ''
                        sh "./mvnw -B -ntp org.owasp:dependency-check-maven:check -DdataDirectory=\${DC_DATA_DIR} ${secProfile}"
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'target/dependency-check-report.*', allowEmptyArchive: true
                    publishHTML(target: [reportDir: 'target', reportFiles: 'dependency-check-report.html',
                                         reportName: 'OWASP Dependency-Check', keepAll: true,
                                         alwaysLinkToLastBuild: true, allowMissing: true])
                }
            }
        }

        stage('Package') {
            when { expression { env.RUN_MODE == 'deploy' } }
            steps {
                sh './mvnw -B -ntp package -DskipTests'
                archiveArtifacts artifacts: 'target/finsecure-pay.jar', fingerprint: true
            }
        }

        stage('Container Build') {
            when { expression { env.RUN_MODE == 'deploy' } }
            steps {
                sh '''
                  DOCKER_BUILDKIT=1 docker build \
                    --build-arg APP_VERSION=${IMAGE_TAG} \
                    --build-arg GIT_COMMIT=${GIT_SHORT} \
                    -t ${IMAGE_REPO}:${IMAGE_TAG} \
                    -t ${IMAGE_REPO}:latest .
                  docker image inspect ${IMAGE_REPO}:${IMAGE_TAG} --format 'Built {{.RepoTags}} size={{.Size}}'
                '''
            }
        }

        stage('Image Scan - Trivy') {
            when { expression { env.RUN_MODE == 'deploy' } }
            steps {
                sh '''
                  mkdir -p reports
                  # Full report for evidence (does not fail)
                  trivy image --cache-dir ${TRIVY_CACHE_DIR} --scanners vuln --format table \
                        --output reports/trivy-report.txt ${IMAGE_REPO}:${IMAGE_TAG}
                  # SECURITY GATE #2: block the image if any fixable HIGH/CRITICAL vulnerability exists
                  # (.trivyignore holds only justified, auto-expiring risk acceptances)
                  trivy image --cache-dir ${TRIVY_CACHE_DIR} --scanners vuln --severity HIGH,CRITICAL \
                        --ignore-unfixed --ignorefile .trivyignore --exit-code 1 ${IMAGE_REPO}:${IMAGE_TAG}
                '''
            }
            post {
                always { archiveArtifacts artifacts: 'reports/trivy-report.txt', allowEmptyArchive: true }
            }
        }

        stage('Push - Docker Hub') {
            when { expression { env.RUN_MODE == 'deploy' } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER', passwordVariable: 'DH_TOKEN')]) {
                    sh '''
                      echo "$DH_TOKEN" | docker login -u "$DH_USER" --password-stdin
                      docker push ${IMAGE_REPO}:${IMAGE_TAG}
                      docker push ${IMAGE_REPO}:latest
                      docker logout
                    '''
                }
            }
        }

        // ------------------------------------------------------------- CD ----
        stage('Deploy - EKS') {
            when { expression { env.RUN_MODE == 'deploy' } }
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'aws-creds',
                                     usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY'),
                    string(credentialsId: 'finsecure-api-key', variable: 'FINSECURE_API_KEY')
                ]) {
                    sh '''
                      aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER} --kubeconfig ./kubeconfig
                      export KUBECONFIG=./kubeconfig

                      kubectl apply -f k8s/00-namespace.yaml
                      kubectl apply -f k8s/10-configmap.yaml

                      # Secret is created from Jenkins credentials - never from a file in Git
                      kubectl -n ${K8S_NAMESPACE} create secret generic finsecure-pay-secrets \
                        --from-literal=FINSECURE_API_KEY="${FINSECURE_API_KEY}" \
                        --dry-run=client -o yaml | kubectl apply -f -

                      sed -e "s|IMAGE_PLACEHOLDER|${IMAGE_REPO}:${IMAGE_TAG}|" \
                          -e "s|CHANGE_CAUSE_PLACEHOLDER|Jenkins build ${BUILD_NUMBER} deployed ${IMAGE_TAG}|" \
                          k8s/20-deployment.yaml | kubectl apply -f -
                      kubectl apply -f k8s/30-service.yaml
                      kubectl apply -f k8s/40-monitoring.yaml || echo "Monitoring CRDs not installed yet - skipping"

                      # Wait for the rolling update; auto-rollback if the new version never becomes ready
                      if ! kubectl -n ${K8S_NAMESPACE} rollout status deployment/${APP_NAME} --timeout=180s; then
                        echo "Rollout FAILED - rolling back to previous revision"
                        kubectl -n ${K8S_NAMESPACE} rollout undo deployment/${APP_NAME}
                        kubectl -n ${K8S_NAMESPACE} rollout status deployment/${APP_NAME} --timeout=180s
                        exit 1
                      fi
                      kubectl -n ${K8S_NAMESPACE} rollout history deployment/${APP_NAME}
                      kubectl -n ${K8S_NAMESPACE} get pods -o wide
                    '''
                }
            }
        }

        stage('Rollback - EKS') {
            when { expression { env.RUN_MODE == 'rollback' } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'aws-creds',
                                     usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh '''
                      aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER} --kubeconfig ./kubeconfig
                      export KUBECONFIG=./kubeconfig
                      echo "--- History before rollback ---"
                      kubectl -n ${K8S_NAMESPACE} rollout history deployment/${APP_NAME}
                      if [ -n "${ROLLBACK_TAG}" ]; then
                        kubectl -n ${K8S_NAMESPACE} set image deployment/${APP_NAME} ${APP_NAME}=${IMAGE_REPO}:${ROLLBACK_TAG}
                        kubectl -n ${K8S_NAMESPACE} annotate deployment/${APP_NAME} --overwrite \
                          kubernetes.io/change-cause="Jenkins build ${BUILD_NUMBER} ROLLBACK to ${ROLLBACK_TAG}"
                      else
                        kubectl -n ${K8S_NAMESPACE} rollout undo deployment/${APP_NAME}
                      fi
                      kubectl -n ${K8S_NAMESPACE} rollout status deployment/${APP_NAME} --timeout=180s
                      echo "--- History after rollback ---"
                      kubectl -n ${K8S_NAMESPACE} rollout history deployment/${APP_NAME}
                    '''
                }
            }
        }

        stage('Smoke Test') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'aws-creds',
                                     usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh '''
                      export KUBECONFIG=./kubeconfig
                      HOST=$(kubectl -n ${K8S_NAMESPACE} get svc ${APP_NAME} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
                      echo "External endpoint: http://${HOST}"
                      for i in $(seq 1 30); do
                        if curl -fsS --max-time 5 "http://${HOST}/health"; then echo; exit 0; fi
                        echo "Waiting for load balancer... ($i)"; sleep 10
                      done
                      echo "Smoke test failed"; exit 1
                    '''
                }
            }
        }
    }

    post {
        success {
            emailext(
                to: "${env.NOTIFY_EMAIL}",
                subject: "SUCCESS: ${env.JOB_NAME} ${currentBuild.displayName}",
                mimeType: 'text/html',
                body: """<p>Pipeline <b>succeeded</b>.</p>
                         <p>Mode: ${env.RUN_MODE}<br/>Image: ${env.IMAGE_REPO}:${env.IMAGE_TAG}<br/>
                         Commit: ${env.GIT_SHORT}</p>
                         <p><a href="${env.BUILD_URL}">Open build</a></p>""")
        }
        failure {
            emailext(
                to: "${env.NOTIFY_EMAIL}",
                subject: "FAILED: ${env.JOB_NAME} ${currentBuild.displayName}",
                mimeType: 'text/html',
                attachLog: true,
                body: """<p>Pipeline <b>FAILED</b> - deployment was blocked.</p>
                         <p>Commit: ${env.GIT_SHORT}</p>
                         <p>Check the failing stage (tests / quality gate / security scan) in the
                         <a href="${env.BUILD_URL}console">console log</a>.</p>""")
        }
        always {
            sh 'rm -f kubeconfig || true'
            sh 'docker image prune -f || true'
        }
    }
}

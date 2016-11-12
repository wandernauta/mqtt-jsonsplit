node {
  stage 'checkout'
  checkout scm

  stage 'check syntax'
  sh 'python3 -m py_compile mqttsplit.py'
}

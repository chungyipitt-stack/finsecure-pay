// Configures Jenkins e-mail (Mailer + Email Extension) for Gmail SMTP using the
// 'smtp-creds' credential created by JCasC - no password appears in this script.
import jenkins.model.Jenkins
import com.cloudbees.plugins.credentials.CredentialsProvider
import com.cloudbees.plugins.credentials.common.StandardUsernamePasswordCredentials

def j = Jenkins.get()
def cred = CredentialsProvider.lookupCredentialsInItemGroup(
        StandardUsernamePasswordCredentials, j, null, []).find { it.id == 'smtp-creds' }
assert cred : 'smtp-creds credential not found'

// Classic Mailer (used by "Test configuration")
def mailer = j.getDescriptorByType(hudson.tasks.Mailer.DescriptorImpl)
mailer.setSmtpHost('smtp.gmail.com')
mailer.setSmtpPort('587')
mailer.setUseSsl(false)
mailer.setUseTls(true)
mailer.setSmtpAuth(cred.username, cred.password.plainText)
mailer.setReplyToAddress(cred.username)
mailer.save()

// Email Extension (used by emailext in the Jenkinsfile)
def ext = j.getDescriptorByType(hudson.plugins.emailext.ExtendedEmailPublisherDescriptor)
def acct = new hudson.plugins.emailext.MailAccount()
acct.setSmtpHost('smtp.gmail.com')
acct.setSmtpPort('587')
acct.setCredentialsId('smtp-creds')
acct.setUseTls(true)
ext.setMailAccount(acct)
ext.setDefaultReplyTo(cred.username)
ext.save()

// Admin e-mail = sender address
def loc = jenkins.model.JenkinsLocationConfiguration.get()
loc.setAdminAddress("FinSecure Jenkins <${cred.username}>")
loc.save()

println "E-mail configured: smtp.gmail.com:587 TLS as ${cred.username}"

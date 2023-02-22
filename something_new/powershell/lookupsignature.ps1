$appid = "appid"

Connect-ExchangeOnline -AppId $appid -CertificateThumbprint "thumbprint" -Organization "org.onmicrosoft.com"

get-MailboxMessageConfiguration -Identity "email@contoso.com" | Select-Object -ExpandProperty SignatureHtml
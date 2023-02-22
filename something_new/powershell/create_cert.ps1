$mycert = New-SelfSignedCertificate -DnsName "yourdomain" -CertStoreLocation "cert:\LocalMachine\My" -NotAfter (Get-Date).AddYears(1) -KeySpec KeyExchange

$mycert | Export-Certificate -FilePath mycert.cer
$mycert | Export-PfxCertificate -FilePath mycert.pfx -Password $(ConvertTo-SecureString -String "SomeP@ss" -AsPlainText -Force)
echo 'DEPLOYING HEROKU APP'
heroku create
heroku container:push web
heroku container:release web
heroku open
echo '[CTRL + C TO EXIT LOG]'
heroku logs --tail


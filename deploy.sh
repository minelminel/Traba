echo 'DEPLOYING HEROKU APP'
heroku create
heroku container:push web
heroku container:release web
heroku open
heroku logs --tail


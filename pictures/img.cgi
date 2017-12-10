#!/bin/sh

if [ -n "$(echo "$HTTP_ACCEPT" | grep 'application/xhtml.xml')" ]; then
    echo 'Content-Type: application/xhtml+xml; charset=UTF-8'
else
    echo 'Content-Type: text/html; charset=UTF-8'
fi
echo

i="$(echo "$QUERY_STRING" | cut -d. -f1)"
if [ -e "alt/$i" ]; then
    title="$(cat alt/$i)"
else
    title="$i"
fi

cat <<END
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <link rel="icon" type="image/png" href="/favicon.png"/>
        <title>${title}</title>
    </head>
    <body>
        <h1>Images of Aftereight's weather station</h1>
        <p><a href=".">Back to image gallery</a></p>
END

if [ -n "$(echo "$QUERY_STRING" | grep "'")" ]; then
    echo "Evil detected"
    exit 1
fi

if [ -n "$(echo "$QUERY_STRING" | grep -E '.*\.(mp4|ogv)$' )" ]; then
    echo "        <video src='$QUERY_STRING' preload='' controls=''/>"
else
    echo "        <img src='$QUERY_STRING' alt='$title'/>"
fi

cat <<END
        <p>${title}</p>
    </body>
</html>
END


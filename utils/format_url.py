def format_url(url, *args):
    if not args:
        return url

    url = url.replace(" ", "%20")

    i = 0
    for arg in args:
        arg = arg.replace(" ", "%20")
        if i == 0:
            url += f'?{arg}'
        else:
            url += f'&{arg}'
        i+=1

    return url


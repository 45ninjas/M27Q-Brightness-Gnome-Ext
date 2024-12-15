# This is a really simple python script. It takes one optional argument, monitor
# brightness 0 to 100. It sets and prints the monitor's brightness. Exists with
# 2 if no monitor is found.

try:
    # https://gist.github.com/wadimw/4ac972d07ed1f3b6f22a101375ecac41
    from m27q import MonitorControl
    from sys import argv

    with MonitorControl() as m:
        if len(argv) == 2:
            if argv[1].isdecimal():
                percent = int(argv[1])
                m.set_brightness(percent)
            elif argv[1] != "false":
                print("usage: " + argv[0] + " <brightness:0-100>")

        print(m.get_brightness())

except IOError as e:
    # No monitor was connected (or there's no permission to access it)
    print("No Monitor Found")
    exit(2)

except Exception as e:
    # There is another error, just print it. Let the extension decide what to
    # do with it.
    print(e)
    exit(1)
    
exit(0)

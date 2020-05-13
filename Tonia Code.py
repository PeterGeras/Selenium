import timeit


def files_handling():
    import files_handling
    files_handling.main()


def xero_download():
    import xero_download
    xero_download.main()


def main():
    print("START - MAIN")
    start = timeit.default_timer()

    # xero_download()
    files_handling()

    stop = timeit.default_timer()
    print("END - MAIN")

    print('Time: ', stop - start)

    return True


if __name__ == '__main__': main()

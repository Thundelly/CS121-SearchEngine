import os


def main():
    count = 0

    if not os.path.exists('./DEV/'):
        print('Please put the DEV folder in the root of the project.')
    else:
        folder = 'DEV'
        for root, dirs, files in os.walk(folder):
            for filename in files:
                if filename.endswith('.json'):
                    print(f'{count}.json')
                    os.rename(os.path.join(root, filename),
                              os.path.join(root, f'{count}.json'))
                    count += 1

        print(f'\n{count} files renamed.')


if __name__ == "__main__":
    main()

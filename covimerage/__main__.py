from covimerage import MergedProfiles, Profile


def main():
    # p = Profile('/tmp/profile.vim')

    import glob

    profiles = []
    for f in glob.glob('/tmp/neomake-profile-*.txt'):
        p = Profile(f)
        p.parse()
        profiles.append(p)

    m = MergedProfiles(profiles)

    for fname, lines in m.lines.items():
        for [lnum, line] in lines.items():
            print('%s:%5d:%s:%s' % (
                fname, lnum, line.count if line.count is not None else '-',
                line.line))
            # for s in self.scripts:
            #     print(s)
            #     for lnum, line in s.lines.items():
            #         print('{:5}: {}'.format(lnum, line))


if __name__ == "__main__":
    main()

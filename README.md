# DocManager
[![Build Status](https://travis-ci.org/openSUSE/docmanager.svg?branch=develop)](https://travis-ci.org/openSUSE/docmanager)
[![codecov.io](http://codecov.io/github/openSUSE/docmanager/coverage.svg?branch=develop)](http://codecov.io/github/openSUSE/docmanager?branch=develop)
[![Code Health](https://landscape.io/github/openSUSE/docmanager/develop/landscape.svg?style=flat)](https://landscape.io/github/openSUSE/docmanager/develop)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/openSUSE/docmanager/badges/quality-score.png?b=develop)](https://scrutinizer-ci.com/g/openSUSE/docmanager/?branch=develop)

DocManager is a tool to manage meta-information within DocBook 5
documents. You can add, delete, edit, and query meta information.
Each meta-information is stored in the `info` element in the
DocManager namespace.

### Repositories
  1. Stable Repository: https://build.opensuse.org/package/show/Documentation:Tools/docmanager
  2. Unstable Repository: https://build.opensuse.org/package/show/Documentation:Tools:Develop/docmanager

### Usage
  1. **Adding or editing meta-information**

      ```
      $ docmanager set -p maintainer=test_name -p version=test_version test_file1.xml test_file2.xml
      ```

  2. **Deleting meta-information**

      ```
      $ docmanager del -p maintainer,version test_file1.xml test_file2.xml
      ```

  3. **Get meta-information**

      ```
      $ docmanager get -p maintainer test_file1.xml
      value_of_property_maintainer
      ```

  Do not provide properties if you want to get all information.

  4. **Analyze meta-information**

      ```
      $ docmanager analyze -qf "This file ({os.file}) is maintained by {maintainer} and has the priority {priority}." example1.xml example2.xml
      ```
      Example output for each file:
      ```
      This file (example1.xml) is maintained by mschnitzer and has the priority 10.
      This file (example2.xml) is maintained by toms and has the priority 5.
      ```

### Developers
- [Rick Salevsky](https://github.com/RSalevsky)
- [Manuel Schnitzer](https://github.com/mschnitzer)
- [Thomas Schraitle](https://github.com/tomschr)

### Contribution
  1. Create a branch if you have access otherwise fork it.
  2. Make your changes.
  3. Create a pull request.
  4. Done! Your changes will be reviewed as soon as possible.

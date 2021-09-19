from awesome_crawler.awesome_crawler import extract


def test_extract() -> None:
    markdown = exampleMarkdown()

    actual = extract(markdown)
    assert len(actual) == 20

    deepfake = next(filter(lambda i: i.name == "DeepfakeHTTP", actual))

    assert deepfake.name == "DeepfakeHTTP"
    assert deepfake.source == "https://github.com/xnbox/DeepfakeHTTP"
    assert "DeepfakeHTTP is a web server" in deepfake.description


def exampleMarkdown() -> str:
    return """
![](https://github.com/TheJambo/awesome-testing/blob/master/AwesomeTesting.jpg?raw=true)
# Awesome Testing [![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)
> A curated list of testing software, extensions and resources

## Foreword
This is intended to be a curation of resources for the new among the software testing community. It is not tailored to a specific area (Usability/Performance) or role (Automation/Management). The idea is that you could hand this list to a CS graduate and it would greatly improve their testing skills, efficiency and overall breadth of knowledge. Note that this is for all areas of software testing after the code in question is written (no unit tests/static analysis!).

Finally, I'm sure everyone who reads this list has one thing they want to add. Please read the [How to Contribute](https://github.com/TheJambo/awesome-testing/blob/master/CONTRIBUTING.md) page and add to the list. :)

## Contents

- [Software](#software)
- [Books](#books)
- [Training](#training)
- [Blogs](#blogs)
- [Newsletters](#newsletters)
- [Suggested Awesome Lists](#suggested-awesome-lists)
- [QA & Testing Road Map](#qa-and-testing-road-map)
- [Others](#Others)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)
- [License](#license)


## Software

### Security
- [BeEF](http://beefproject.com/) - Manipulate the browser exploiting any XSS vulns you find.
- [OWASP ZAP](https://github.com/zaproxy/zaproxy) - This intercepting proxy allows you to see all HTTP traffic and manipulate it in real time. Easy to scan, catalog and exploit security issues.

### Make your life easier
- [Courgette](https://courgette-testing.com) - Beautifully simple UI testing. Proper declarative BDD scenarios using Gherkin, Gherkin templates and composable YAML-style page and component objects.
- [BareTail](https://www.baremetalsoft.com/baretail/) - Brings the tail linux command to Windows, coloured lines and REGEX search and loads of other features.
- [ProxySwitcher](https://chrome.google.com/webstore/detail/proxy-switcher-manager/onnfghpihccifgojkpnnncpagjcdbjod) - We all have to mess with proxies, this makes it a lot easier when using Test/Prod/localhost proxies.
- [Full Page Screenshot](https://chrome.google.com/webstore/detail/full-page-screen-capture/fdpohaocaechififmbbbbbknoalclacl) - For when PrintScreen isn't big enough.
- [Form Filler](https://chrome.google.com/webstore/detail/form-filler/bnjjngeaknajbdcgpfkgnonkmififhfo) - Large forms can be really irritating to fill out each time, speed it up with dummy data.
- [Bug Magnet](https://chrome.google.com/webstore/detail/bug-magnet/efhedldbjahpgjcneebmbolkalbhckfi) - Suggests values based on the field type.
- [Check All](https://chrispederick.com/work/web-developer/) - "Select All" is often not available. Why not bring your own?
- [Xmind](http://www.xmind.net/) - The best (free) Mindmapping tool for documenting your tests.
- [TestLink](https://github.com/TestLinkOpenSourceTRMS/testlink-code) - Open Source test case management system
- [Fluxguard](https://fluxguard.com) - Screenshot pixel and DOM change comparisons and regressions.
- [recheck-web](https://github.com/retest/recheck-web) - Open Source change comparison tool with local Golden Masters, git-like ignore syntax and "unbreakable selenium" tests.
- [Kiwi TCMS](https://github.com/kiwitcms/Kiwi) - Open Source test case management system.
- [Captura](https://github.com/MathewSachin/Captura) - Open Source video recording tool.
- [QA Wolf](https://github.com/qawolf/qawolf) - Open Source Node.js library for creating browser tests 10x faster.
- [Online decision table service](http://decision-table.com/) - full test coverage by generating cases with simple Decision Table technique.
- [Synth](https://github.com/getsynth/synth) - Open Source test data generator.
- [Requestly](https://requestly.io/) - A lightweight proxy as a browser extension & desktop app to intercept & modify network requests. You can Modify Headers, Redirect Url, Mock API response, Delay/Throttle requests, etc.
- [DeepfakeHTTP](https://github.com/xnbox/DeepfakeHTTP) - DeepfakeHTTP is a web server that uses HTTP dumps as a source for responses. This tool allows you to test clients against REST, GraphQL, and other APIs.
"""

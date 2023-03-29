#! /usr/bin/bash
# Команда для создания красивого лога
git log --pretty="%an: %ci %n %s%n" > GitChangeLog.md 
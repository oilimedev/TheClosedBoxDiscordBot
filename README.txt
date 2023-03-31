ROO Reminder Bot Readme

This bot is designed to help remind users to perform certain actions related to Leppa Berries and Gracidea Flowers in PokeMMO. It uses Discord's API to communicate with users and schedule reminders.

Usage
This bot has the following commands:

!leppa
Reminds the user to harvest their Leppa Berries in 20 hours.

Example usage: !leppa

!water (hours)
Reminds the user to water their berries after a specified duration (in hours).

Example usage: !water 6

This will remind the user to water their berries in 6 hours.

!myalerts
Lists all of the user's active reminders.

Example usage: !myalerts

!cancelalerts
Cancels all of the user's active reminders.

Example usage: !cancelalerts

NOTE
The !leppa command cancels out any outstanding !water reminders.
This means you should set a !leppa reminder before setting a !water reminder.
!water reminders can also be set on their own just not before a !leppa reminder.

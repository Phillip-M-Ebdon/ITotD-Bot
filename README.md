# Imperial Thought of the Day

This bot was an afternoon project to send a daily "Thought of the Day" taken from Warhammer 40k.

The bot is an unofficial project.

To add the bot to your sever use the link below:  
https://discord.com/oauth2/authorize?client_id=867251886674542662&scope=bot&permissions=0


Commands are only accessible for the servers owner.  
Arguments should be separated by a space.
The prefix is `*`

Commands:
 - channel - Set the text channel the bot posts in, provide the exact name as an argument.   
   example: *channel my-channel
   
 - time - Set the time of day based on UTC for the quote to appear. Provide two arguments, the hours, and the minutes.  
   example: *time 9 45  
   minutes will be rounded down to the next multiple of 5.
   

When your server is first added, no time or channel is set.
In this instance, you will receive posts in your system-channel, or failing that in the first available text channel.
The quotes will default to 00:00 UTC

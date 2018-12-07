# PriCoSha
Andrew Lee  asl529@nyu.edu
Daniel Chung  dc3598@nyu.edu

PriCoSha is a database system that allows for publicly or privately sharing content items. Users can register for an account or just view the public content. However, in order to use all the features, you must register and login. You can create your own group of friends or colleagues and share specific content within that group. You can also tag individuals who are a part of your FriendGroup. PriCoSha allows you to sort and customize the amount of involvement of others. 

We implemented:
- Login and Registration
- Viewing Public Content
- Posting Content Publicly or Privately
- Managing Friends
- Managing Tags
Our optional features were to:
Create your own FriendGroup - You would create FriendGroups, and be able to add registered people to these group which would allow you to share with your group and tag individuals in content posts
Delete unwanted friends from your groups- You would remove any wanted individuals from the FriendGroups, therefore removing any shared posts/tags
These are good features to add to PriCoSha because it allows for increased flexibility in privacy or publicity as you desire. 

Andrew was primarily in charge of:
- Login and Registration
- Posting Content
- Managing Friends
- Creating FriendGroup (optional)

SQL Queries used:
- SELECT * FROM Friendgroup WHERE owner_email = %s AND fg_name = %s
- INSERT INTO Friendgroup VALUES(%s, %s, %s)
- INSERT INTO Belong VALUES(%s, %s, %s)

Daniel was primarily in charge of:
- Viewing Public Content
- Managing Tags
- Deleting Unwanted Friends (optional)

SQL Queries used:
- SELECT * FROM Belong WHERE owner_email=%s AND email=%s
- DELETE FROM Belong WHERE owner_email=%s AND email=%s
- DELETE FROM Tag WHERE email_tagger IN (SELECT email FROM Belong WHERE owner_email = %s) AND email_tagged=%s

However, we have mainly worked on most parts together.

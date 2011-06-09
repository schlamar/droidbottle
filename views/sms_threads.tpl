<ul>
%for address in addresses:
    <li><a href="/sms/{{address}}">{{address}}</a></li>
%end
</ul>
%rebase layout title='SMS'

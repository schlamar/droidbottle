  <script type="text/javascript">
window.onload=toBottom;

function toBottom()
{
window.scrollTo(0, document.body.scrollHeight);
}
  </script>
<ul>
%for msg in messages:
    % adr = 'Me' if msg.sent else address
    <li><b>{{adr}}</b>: {{msg.body}}</li>
%end
</ul>
<a href=/sms/{{address}}/new>reply</a>
<a href=/sms>back</a>
%rebase layout title='SMS with %s' % address

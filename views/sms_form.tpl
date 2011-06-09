<p>Send sms to "{{address}}".</p>
<form method=POST action=/sms/{{address}}/new>
<textarea rows=5 cols=40 name=body></textarea><br />
<input type=submit />
</form>
%rebase layout title='SMS to %s' % address

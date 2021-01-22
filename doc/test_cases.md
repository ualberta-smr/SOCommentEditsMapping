# Test cases

<ol>
<li> <b>Answer has a high upvote count</b>

StackOverflow Post: 16184827

| Comment ID  | Mapped Edit | Code Match |
| ----------- | ----------- | ---------- |
| 914779      |      2      | {'sum += lookup[data[j]]'} |
</li>
<li> <b>Answer has low upvote count</b>

StackOverflow Post: 44880776

| Comment ID  | Mapped Edit | Code Match |
| ----------- | ----------- | ---------- |
|   76741141  |      3      | {'nextLine()', 'nextDouble', 'keyboard.nextLine', 'keyboard.nextLine()'} |
</li>
<li> <b>Answer has an old creation date</b>

StackOverflow Post: 35666

| Comment ID  | Mapped Edit | Code Match |
| ----------- | ----------- | ---------- |
| 914779      |      3      | {'Contains(TKey item)'} |
| 914786      |      3      | {'return _dict.Contains(item);', '_dict.Contains', 'return _dict.Contains(item)', 'Contains(item)', '_dict.Contains(item)'} |
</li>
<li> <b>Answer has recent creation date</b>

StackOverflow Post: 25915251

| Comment ID  | Mapped Edit | Code Match |
| ----------- | ----------- | ---------- |
|   77891281  |      2      | {"if (yourChar == '\\r' \|\| yourChar == '\\n')"} |
</li>
<li> <b>Lots of Edits/ Lots of Comments</b>

StackOverflow Post: 33507565

| Comment ID  | Mapped Edit | Code Match |
| ----------- | ----------- | ---------- |
|   65554558  |      5      | {'clone()'} |
|   65556841  |      5      | {'clone()'} |
|   74004641  |      9      | {'map(Dog::new)'} |
</li>
<li><b>Lots of Edits/ Low Comments</b>

StackOverflow Post: 9554482

| Comment ID  | Mapped Edit | Code Match |
| ----------- | ----------- | ---------- |
|   12109641  |      4      | {'foo()', 'Base', 'x', 'Base()'} |
|   12109641  |      6      | {'Base', 'x', 'foo()', 'x=1', 'Base()'} |
</li>
<li> <b>Low edits/ Lots of Comments</b>
StackOverflow Post: 21616398

| Comment ID  | Mapped Edit | Code Match |
| ----------- | ----------- | ---------- |
|  36642065   |      2      | {'forEach(System.out::println)', 'Arrays.stream(strArray)', 'System.out', 'Arrays.stream', 'stream(strArray)'} |
|  40622086   |      2      | {'System.out', 'System.out::println'} |
|  59284899   |      2      | {'forEach(System.out::println)', 'Arrays.stream(strArray)', 'System.out', 'Arrays.stream', 'stream(strArray)'} |
|  60134092   |      2      |  {'Stream.of'} |
</li>
<li> <b>Low Edits/ Low comments</b>

StackOverflow Post: 24810414

| Comment ID  | Mapped Edit | Code Match |
| ----------- | ----------- | ---------- |
|  38693783   |      2      | {'null', 'return null'} |
|  38693783   |      4      | {'null', 'return null'} |
|  38693783   |      5      | {'null', 'return null'} |
</li>
<li> <b>Random 1</b>

StackOverflow Post: 24947520

| Comment ID  | Mapped Edit | Code Match |
| ----------- | ----------- | ---------- |
|  38772735   |      3      | {'itemsList.getString(i)', 'itemList', 'itemsList.getString', 'itemsList', 'item = itemsList'} |
|  38773611   |      3      | {'itemList'} |
</li>
<li> <b>Random 2</b> 

StackOverflow Post: 44187121

| Comment ID  | Mapped Edit | Code Match |
| ----------- | ----------- | ---------- |
|  75389161   |      2      | {'Month.values', 'values()', 'Month.values()'} |
</li>
</ol>
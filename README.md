#dbp\_taxonomy\_fetcher

This free software queries a sparql endpoint with dbpedia data and collects the
taxonomy beginning at a given root node. Then the Wikipedia articles belonging
to the taxonomy are loaded and their abstracts are stored as well. The
resulting python object can be stored in a pickled file, the abstracts can be
exported as text files.

Run *python dbp\_taxonomy\_fetcher.py --help* to see the available options.


##Licence

This file is part of dbp\_taxonomy\_fetcher.

dbp\_taxonomy\_fetcher is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

dbp\_taxonomy\_fetcher is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with dbp\_taxonomy\_fetcher. If not, see <http://www.gnu.org/licenses/>.

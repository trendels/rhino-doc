#!/usr/bin/env python
"""
Pandoc filter to insert automatic links to classes, functions and modules.
"""
import os.path

from pandocfilters import toJSONFilter, Code, Link

links = {}

def autolink(key, value, format, meta):
    if 'links' in meta and not links:
        links_file = meta['links']['c']
        with open(links_file) as f:
            for line in f:
                name, target = line.strip().split('|', 1)
                links[name] = target
        links[None] = None   # Create dummy key to links is True in all cases
    if key == 'Code':
        # For 'Code', the value has the form (attr_list, str),
        # where attr_list is (identifiers, class_list, kv)
        # and kv is a list of (key, value) tuples
        #
        # For 'Link', the value has the form (children, target)
        # where children is the list of (inline) child nodes
        # and target is a (URL, link_title) tuple.
        #
        # Source:
        # http://hackage.haskell.org/package/pandoc-types-1.12.4.1/docs/Text-Pandoc-Definition.html#t:Inline
        (attr_list, string) = value
        href = None
        if string in links:
            href = 'api/' + links[string]
        elif 'module' in meta:
            # TODO why is module a list but link_prefix is not?
            module_name = meta['module']['c'][0]['c']
            # TODO allow '.foo', '..foo.bar', etc.
            link_target = module_name + '.' + string
            if link_target in links:
                href = 'api/' + links[link_target]
        if href is not None:
            if 'link_prefix' in meta:
                link_prefix = meta['link_prefix']['c']
                if '#' in href:
                    path, anchor = href.split('#', 1)
                else:
                    path, anchor = href, None
                href = link_prefix + path
                if anchor:
                    href += '#' + anchor
            return Link([Code(attr_list, string)], [href, ''])  # TODO add title

if __name__ == '__main__':
    toJSONFilter(autolink)

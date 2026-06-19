# Makefile delegating to top-level Makefile for services

# Any target called here forwards to the root Makefile in /data/coolify
%:
	@$(MAKE) -C .. $@

# Media Nginx service delegation target
media-nginx:
	@$(MAKE) -C ../proxy media-nginx

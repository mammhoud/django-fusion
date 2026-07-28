"""
Domain Reachability Tests for VResume and CTC Research

Tests check:
- HTTP status codes
- Content integrity
- Style tag loading
- Meta tags
- Error handling
- Performance metrics
"""

import requests
import re
from typing import Dict, List, Tuple
import pytest
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time


class DomainReachabilityTest:
    """Test domain reachability and content integrity."""
    
    # Test domains
    DOMAINS = {
        'vresume': {
            'url': 'https://vresume.structa.cloud',
            'paths': [
                '/',
                '/blog/',
                '/contact/',
                '/admin/',
            ],
        },
        'ctc': {
            'url': 'https://ctc-research.com',
            'paths': [
                '/',
                '/research/',
                '/about/',
            ],
        },
        'structa': {
            'url': 'https://structa.cloud',
            'paths': [
                '/',
                '/admin/',
                '/about/',
            ],
        },
        'lms': {
            'url': 'https://lms-demo.com',
            'paths': [
                '/',
                '/blog/',
                '/admin/',
            ],
        },
        'media_structa': {
            'url': 'https://media.structa.cloud',
            'paths': [
                '/',
                '/static/images/logo.png',
            ],
        },
        'media_ctc': {
            'url': 'https://media.ctc-research.com',
            'paths': [
                '/',
                '/static/images/logo.png',
            ],
        },
        'media_lms': {
            'url': 'https://media.lms-demo.com',
            'paths': [
                '/',
                '/static/images/logo.png',
            ],
        },
        'media_vresume': {
            'url': 'https://media.vresume.structa.cloud',
            'paths': [
                '/',
                '/static/images/logo.png',
            ],
        },
    }
    
    # Timeouts
    CONNECT_TIMEOUT = 10
    READ_TIMEOUT = 30
    
    def get_session(self) -> requests.Session:
        """Create requests session with headers."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        return session
    
    def test_domain_reachability(self) -> Dict[str, Dict]:
        """Test if domains are reachable."""
        results = {}
        session = self.get_session()
        
        for domain_name, domain_config in self.DOMAINS.items():
            url = domain_config['url']
            
            try:
                start_time = time.time()
                response = session.get(
                    url,
                    timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT),
                    allow_redirects=True,
                    verify=False,  # Allow self-signed certs
                )
                elapsed_time = time.time() - start_time
                
                results[domain_name] = {
                    'reachable': response.status_code < 500,
                    'status_code': response.status_code,
                    'response_time': elapsed_time,
                    'content_length': len(response.content),
                    'url': url,
                    'error': None,
                }
            except requests.exceptions.Timeout:
                results[domain_name] = {
                    'reachable': False,
                    'status_code': None,
                    'response_time': None,
                    'content_length': 0,
                    'url': url,
                    'error': 'Timeout',
                }
            except requests.exceptions.ConnectionError as e:
                results[domain_name] = {
                    'reachable': False,
                    'status_code': None,
                    'response_time': None,
                    'content_length': 0,
                    'url': url,
                    'error': f'Connection Error: {str(e)[:100]}',
                }
            except Exception as e:
                results[domain_name] = {
                    'reachable': False,
                    'status_code': None,
                    'response_time': None,
                    'content_length': 0,
                    'url': url,
                    'error': f'Error: {str(e)[:100]}',
                }
        
        return results
    
    def test_style_tags(self, url: str) -> Dict[str, any]:
        """Test if style tags are loaded correctly."""
        try:
            response = requests.get(
                url,
                timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT),
                verify=False,
            )
            
            if response.status_code != 200:
                return {
                    'has_styles': False,
                    'style_count': 0,
                    'link_count': 0,
                    'inline_styles': 0,
                    'total_css_references': 0,
                    'error': f'Non-200 status: {response.status_code}',
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Count style tags
            style_tags = soup.find_all('style')
            link_tags = soup.find_all('link', {'rel': 'stylesheet'})
            
            # Count inline styles
            inline_styles = len(soup.find_all(style=True))
            
            # Check for critical CSS
            head = soup.find('head')
            has_css = bool(link_tags or style_tags)
            
            return {
                'has_styles': has_css,
                'style_count': len(style_tags),
                'link_count': len(link_tags),
                'inline_styles': inline_styles,
                'total_css_references': len(style_tags) + len(link_tags),
                'error': None,
            }
        except Exception as e:
            return {
                'has_styles': False,
                'style_count': 0,
                'link_count': 0,
                'inline_styles': 0,
                'total_css_references': 0,
                'error': str(e)[:100],
            }
    
    def test_meta_tags(self, url: str) -> Dict[str, any]:
        """Test meta tags."""
        try:
            response = requests.get(
                url,
                timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT),
                verify=False,
            )
            
            if response.status_code != 200:
                return {'error': f'Non-200 status: {response.status_code}'}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get meta tags
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name:
                    meta_tags[name] = content
            
            return {
                'meta_count': len(meta_tags),
                'has_viewport': 'viewport' in meta_tags,
                'has_charset': any('charset' in str(m) for m in soup.find_all('meta')),
                'meta_tags': meta_tags,
                'error': None,
            }
        except Exception as e:
            return {
                'meta_count': 0,
                'has_viewport': False,
                'has_charset': False,
                'meta_tags': {},
                'error': str(e)[:100],
            }
    
    def test_content_integrity(self, url: str) -> Dict[str, any]:
        """Test content for errors and integrity."""
        try:
            response = requests.get(
                url,
                timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT),
                verify=False,
            )
            
            if response.status_code != 200:
                return {
                    'valid': False,
                    'errors': [f'Non-200 status: {response.status_code}'],
                }
            
            content = response.text
            errors = []
            
            # Check for common errors
            error_patterns = [
                (r'500 Server Error', 'Server error detected'),
                (r'404 Not Found', 'Page not found'),
                (r'Traceback', 'Python traceback found'),
                (r'SyntaxError', 'Syntax error found'),
                (r'AttributeError', 'Attribute error found'),
                (r'TypeError', 'Type error found'),
                (r'<h1>Error</h1>', 'Error page detected'),
                (r'<!DOCTYPE html>\s*<html>\s*<head>\s*</head>\s*<body>\s*</body>\s*</html>', 'Empty HTML'),
            ]
            
            for pattern, error_msg in error_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    errors.append(error_msg)
            
            # Check for basic HTML structure
            soup = BeautifulSoup(content, 'html.parser')
            has_html = bool(soup.find('html'))
            has_head = bool(soup.find('head'))
            has_body = bool(soup.find('body'))
            has_title = bool(soup.find('title'))
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'has_html': has_html,
                'has_head': has_head,
                'has_body': has_body,
                'has_title': has_title,
                'content_length': len(content),
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [str(e)[:100]],
            }
    
    def test_response_headers(self, url: str) -> Dict[str, any]:
        """Test response headers."""
        try:
            response = requests.head(
                url,
                timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT),
                allow_redirects=True,
                verify=False,
            )
            
            headers = dict(response.headers)
            
            return {
                'content_type': headers.get('Content-Type'),
                'content_length': headers.get('Content-Length'),
                'server': headers.get('Server'),
                'cache_control': headers.get('Cache-Control'),
                'x_powered_by': headers.get('X-Powered-By'),
                'all_headers': headers,
            }
        except Exception as e:
            return {
                'error': str(e)[:100],
            }
    
    def test_all_paths(self) -> Dict:
        """Test all paths for all domains."""
        results = {}
        session = self.get_session()
        
        for domain_name, domain_config in self.DOMAINS.items():
            results[domain_name] = {}
            
            for path in domain_config['paths']:
                url = urljoin(domain_config['url'], path)
                
                try:
                    response = session.get(
                        url,
                        timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT),
                        verify=False,
                    )
                    
                    results[domain_name][path] = {
                        'status': response.status_code,
                        'success': response.status_code < 400,
                        'content_length': len(response.content),
                    }
                except Exception as e:
                    results[domain_name][path] = {
                        'status': None,
                        'success': False,
                        'error': str(e)[:100],
                    }
        
        return results
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        report = []
        report.append("=" * 80)
        report.append("DOMAIN REACHABILITY TEST REPORT")
        report.append("=" * 80)
        
        # Test 1: Domain Reachability
        report.append("\n1. DOMAIN REACHABILITY")
        report.append("-" * 40)
        reachability = self.test_domain_reachability()
        for domain, result in reachability.items():
            report.append(f"\n{domain.upper()}:")
            report.append(f"  URL: {result['url']}")
            report.append(f"  Reachable: {result['reachable']}")
            report.append(f"  Status Code: {result['status_code']}")
            report.append(f"  Response Time: {result['response_time']:.2f}s" if result['response_time'] else "  Response Time: N/A")
            report.append(f"  Content Length: {result['content_length']} bytes")
            if result['error']:
                report.append(f"  ERROR: {result['error']}")
        
        # Test 2: Style Tags
        report.append("\n\n2. STYLE TAG LOADING")
        report.append("-" * 40)
        for domain_name, domain_config in self.DOMAINS.items():
            url = domain_config['url']
            styles = self.test_style_tags(url)
            report.append(f"\n{domain_name.upper()}:")
            report.append(f"  URL: {url}")
            report.append(f"  Has Styles: {styles['has_styles']}")
            report.append(f"  Style Tags: {styles['style_count']}")
            report.append(f"  Link Tags: {styles['link_count']}")
            report.append(f"  Inline Styles: {styles['inline_styles']}")
            report.append(f"  Total CSS References: {styles['total_css_references']}")
            if styles['error']:
                report.append(f"  ERROR: {styles['error']}")
        
        # Test 3: Meta Tags
        report.append("\n\n3. META TAGS")
        report.append("-" * 40)
        for domain_name, domain_config in self.DOMAINS.items():
            url = domain_config['url']
            meta = self.test_meta_tags(url)
            report.append(f"\n{domain_name.upper()}:")
            report.append(f"  Meta Count: {meta.get('meta_count', 0)}")
            report.append(f"  Has Viewport: {meta.get('has_viewport', False)}")
            report.append(f"  Has Charset: {meta.get('has_charset', False)}")
            if meta.get('error'):
                report.append(f"  ERROR: {meta['error']}")
        
        # Test 4: Content Integrity
        report.append("\n\n4. CONTENT INTEGRITY")
        report.append("-" * 40)
        for domain_name, domain_config in self.DOMAINS.items():
            url = domain_config['url']
            integrity = self.test_content_integrity(url)
            report.append(f"\n{domain_name.upper()}:")
            report.append(f"  Valid: {integrity.get('valid', False)}")
            report.append(f"  Has HTML: {integrity.get('has_html', False)}")
            report.append(f"  Has Head: {integrity.get('has_head', False)}")
            report.append(f"  Has Body: {integrity.get('has_body', False)}")
            report.append(f"  Has Title: {integrity.get('has_title', False)}")
            report.append(f"  Content Length: {integrity.get('content_length', 0)} bytes")
            if integrity.get('errors'):
                report.append(f"  Errors Found: {len(integrity['errors'])}")
                for error in integrity['errors']:
                    report.append(f"    - {error}")
        
        # Test 5: Response Headers
        report.append("\n\n5. RESPONSE HEADERS")
        report.append("-" * 40)
        for domain_name, domain_config in self.DOMAINS.items():
            url = domain_config['url']
            headers = self.test_response_headers(url)
            report.append(f"\n{domain_name.upper()}:")
            report.append(f"  Content-Type: {headers.get('content_type', 'N/A')}")
            report.append(f"  Content-Length: {headers.get('content_length', 'N/A')}")
            report.append(f"  Server: {headers.get('server', 'N/A')}")
            report.append(f"  Cache-Control: {headers.get('cache_control', 'N/A')}")
            report.append(f"  X-Powered-By: {headers.get('x_powered_by', 'N/A')}")
        
        # Test 6: All Paths
        report.append("\n\n6. PATH ACCESSIBILITY")
        report.append("-" * 40)
        all_paths = self.test_all_paths()
        for domain_name, paths in all_paths.items():
            report.append(f"\n{domain_name.upper()}:")
            for path, result in paths.items():
                status = result.get('status', 'N/A')
                success = result.get('success', False)
                status_icon = "✓" if success else "✗"
                report.append(f"  {status_icon} {path}: {status}")
        
        report.append("\n" + "=" * 80)
        return "\n".join(report)


def main():
    """Run all tests and generate report."""
    tester = DomainReachabilityTest()
    report = tester.generate_report()
    print(report)
    
    # Save report
    with open('/tmp/domain_reachability_report.txt', 'w') as f:
        f.write(report)
    
    print("\n✓ Report saved to /tmp/domain_reachability_report.txt")


if __name__ == '__main__':
    main()

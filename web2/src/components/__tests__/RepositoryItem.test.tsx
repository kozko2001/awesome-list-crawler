import { render, screen } from '@testing-library/react';
import { RepositoryItem } from '../RepositoryItem';
import { AppItem } from '@/types/api';

const mockItem: AppItem = {
  name: 'awesome-repo',
  description: 'A really awesome repository for testing',
  source: 'https://github.com/test/awesome-repo',
  list_name: 'awesome-javascript',
  list_source: 'https://github.com/test/awesome-javascript',
  time: '2024-01-15T10:30:00Z',
};

describe('RepositoryItem', () => {
  it('renders repository information correctly', () => {
    render(<RepositoryItem item={mockItem} />);
    
    // Check if repository name is rendered as a link
    const nameLink = screen.getByRole('link', { name: /awesome-repo/i });
    expect(nameLink).toBeInTheDocument();
    expect(nameLink).toHaveAttribute('href', mockItem.source);
    expect(nameLink).toHaveAttribute('target', '_blank');
    
    // Check if description is rendered
    expect(screen.getByText(mockItem.description)).toBeInTheDocument();
    
    // Check if list name is shown as internal link (with new responsive layout)
    expect(screen.getByText('from')).toBeInTheDocument();
    const sourceLink = screen.getByRole('link', { name: 'awesome-javascript' });
    expect(sourceLink).toBeInTheDocument();
    expect(sourceLink).toHaveAttribute('href', '/sources/awesome-javascript');
    
    // Check if date is formatted and shown
    expect(screen.getByText('1/15/2024')).toBeInTheDocument();
  });

  it('applies correct CSS classes for terminal styling', () => {
    const { container } = render(<RepositoryItem item={mockItem} />);
    
    const itemContainer = container.querySelector('[class*="border"]');
    expect(itemContainer).toHaveClass('border');
  });

  it('opens repository link in new tab with security attributes', () => {
    render(<RepositoryItem item={mockItem} />);
    
    const nameLink = screen.getByRole('link', { name: /awesome-repo/i });
    expect(nameLink).toHaveAttribute('rel', 'noopener noreferrer');
    expect(nameLink).toHaveAttribute('target', '_blank');
  });

  it('source link navigates internally', () => {
    render(<RepositoryItem item={mockItem} />);
    
    const sourceLink = screen.getByRole('link', { name: 'awesome-javascript' });
    expect(sourceLink).toHaveAttribute('href', '/sources/awesome-javascript');
    expect(sourceLink).not.toHaveAttribute('target');
    expect(sourceLink).not.toHaveAttribute('rel');
  });
});
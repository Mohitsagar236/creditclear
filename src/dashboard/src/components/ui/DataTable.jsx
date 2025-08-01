/**
 * Enhanced Table Component System
 */
import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  ChevronUp, 
  ChevronDown, 
  Search, 
  Filter, 
  Download,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  ArrowUpDown
} from 'lucide-react';
import Button, { IconButton } from './Button';
import { Input, SearchInput } from './Input';

// Base Table Component
export const Table = ({ 
  children, 
  className = '',
  variant = 'default'
}) => {
  const variantClasses = {
    default: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
    minimal: 'bg-transparent',
    elevated: 'bg-white dark:bg-gray-800 shadow-lg rounded-lg border border-gray-200 dark:border-gray-700'
  };

  return (
    <div className={`overflow-hidden ${variantClasses[variant]} ${className}`}>
      <div className="overflow-x-auto">
        <table className="w-full divide-y divide-gray-200 dark:divide-gray-700">
          {children}
        </table>
      </div>
    </div>
  );
};

// Table Header
export const TableHeader = ({ children, className = '' }) => (
  <thead className={`bg-gray-50 dark:bg-gray-900 ${className}`}>
    {children}
  </thead>
);

// Table Body
export const TableBody = ({ children, className = '' }) => (
  <tbody className={`bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700 ${className}`}>
    {children}
  </tbody>
);

// Table Row
export const TableRow = ({ 
  children, 
  className = '',
  hover = true,
  selected = false,
  onClick
}) => (
  <tr 
    className={`
      ${hover ? 'hover:bg-gray-50 dark:hover:bg-gray-700' : ''}
      ${selected ? 'bg-blue-50 dark:bg-blue-900/20' : ''}
      ${onClick ? 'cursor-pointer' : ''}
      transition-colors duration-150
      ${className}
    `}
    onClick={onClick}
  >
    {children}
  </tr>
);

// Table Header Cell
export const TableHeaderCell = ({ 
  children, 
  className = '',
  sortable = false,
  sortDirection,
  onSort,
  align = 'left'
}) => {
  const alignClasses = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right'
  };

  return (
    <th 
      className={`
        px-6 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider
        ${alignClasses[align]}
        ${sortable ? 'cursor-pointer hover:text-gray-700 dark:hover:text-gray-300' : ''}
        ${className}
      `}
      onClick={sortable ? onSort : undefined}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        {sortable && (
          <span className="flex flex-col">
            {sortDirection === 'asc' ? (
              <ChevronUp className="h-3 w-3" />
            ) : sortDirection === 'desc' ? (
              <ChevronDown className="h-3 w-3" />
            ) : (
              <ArrowUpDown className="h-3 w-3 opacity-50" />
            )}
          </span>
        )}
      </div>
    </th>
  );
};

// Table Cell
export const TableCell = ({ 
  children, 
  className = '',
  align = 'left'
}) => {
  const alignClasses = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right'
  };

  return (
    <td className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100 ${alignClasses[align]} ${className}`}>
      {children}
    </td>
  );
};

// Enhanced Data Table with features
export const DataTable = ({
  data = [],
  columns = [],
  loading = false,
  searchable = true,
  filterable = false,
  sortable = true,
  selectable = false,
  exportable = false,
  pagination = true,
  pageSize = 10,
  className = '',
  onRowClick,
  onRowSelect,
  emptyMessage = "No data available"
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: null });
  const [selectedRows, setSelectedRows] = useState(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState({});

  // Filtered and sorted data
  const processedData = useMemo(() => {
    let filtered = data;

    // Apply search
    if (searchTerm) {
      filtered = filtered.filter(row =>
        columns.some(col => {
          const value = col.accessor ? row[col.accessor] : '';
          return String(value).toLowerCase().includes(searchTerm.toLowerCase());
        })
      );
    }

    // Apply filters
    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        filtered = filtered.filter(row => 
          String(row[key]).toLowerCase().includes(String(value).toLowerCase())
        );
      }
    });

    // Apply sorting
    if (sortConfig.key) {
      filtered.sort((a, b) => {
        const aVal = a[sortConfig.key];
        const bVal = b[sortConfig.key];
        
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return filtered;
  }, [data, searchTerm, sortConfig, filters, columns]);

  // Pagination
  const totalPages = Math.ceil(processedData.length / pageSize);
  const paginatedData = pagination 
    ? processedData.slice((currentPage - 1) * pageSize, currentPage * pageSize)
    : processedData;

  const handleSort = (key) => {
    if (!sortable) return;
    
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedRows(new Set(paginatedData.map((_, index) => index)));
    } else {
      setSelectedRows(new Set());
    }
  };

  const handleRowSelect = (index, checked) => {
    const newSelected = new Set(selectedRows);
    if (checked) {
      newSelected.add(index);
    } else {
      newSelected.delete(index);
    }
    setSelectedRows(newSelected);
    onRowSelect?.(Array.from(newSelected).map(i => paginatedData[i]));
  };

  const handleExport = () => {
    // Simple CSV export
    const headers = columns.map(col => col.header).join(',');
    const rows = processedData.map(row => 
      columns.map(col => col.accessor ? row[col.accessor] : '').join(',')
    ).join('\n');
    
    const csv = `${headers}\n${rows}`;
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'data.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {/* Header skeleton */}
        <div className="flex justify-between items-center">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-48 animate-pulse" />
          <div className="flex space-x-2">
            <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div className="h-8 w-8 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>
        </div>
        
        {/* Table skeleton */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg">
          <div className="h-12 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700" />
          {Array.from({ length: pageSize }).map((_, i) => (
            <div key={i} className="h-16 border-b border-gray-200 dark:border-gray-700 last:border-b-0" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Table Controls */}
      {(searchable || filterable || exportable) && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex flex-1 items-center space-x-4">
            {searchable && (
              <div className="flex-1 max-w-sm">
                <SearchInput
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            )}
            
            {filterable && (
              <IconButton variant="outline" size="sm">
                <Filter className="h-4 w-4" />
              </IconButton>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            {exportable && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleExport}
                className="flex items-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>Export</span>
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Table */}
      <Table variant="elevated">
        <TableHeader>
          <TableRow>
            {selectable && (
              <TableHeaderCell className="w-12">
                <input
                  type="checkbox"
                  checked={selectedRows.size === paginatedData.length && paginatedData.length > 0}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </TableHeaderCell>
            )}
            
            {columns.map((column, index) => (
              <TableHeaderCell
                key={index}
                sortable={sortable && column.sortable !== false}
                sortDirection={sortConfig.key === column.accessor ? sortConfig.direction : null}
                onSort={() => handleSort(column.accessor)}
                align={column.align}
              >
                {column.header}
              </TableHeaderCell>
            ))}
            
            <TableHeaderCell className="w-12">
              <span className="sr-only">Actions</span>
            </TableHeaderCell>
          </TableRow>
        </TableHeader>
        
        <TableBody>
          {paginatedData.length === 0 ? (
            <TableRow>
              <TableCell 
                colSpan={columns.length + (selectable ? 1 : 0) + 1}
                className="text-center py-12 text-gray-500 dark:text-gray-400"
              >
                {emptyMessage}
              </TableCell>
            </TableRow>
          ) : (
            paginatedData.map((row, rowIndex) => (
              <motion.tr
                key={rowIndex}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: rowIndex * 0.05 }}
                className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                onClick={() => onRowClick?.(row, rowIndex)}
              >
                {selectable && (
                  <TableCell>
                    <input
                      type="checkbox"
                      checked={selectedRows.has(rowIndex)}
                      onChange={(e) => handleRowSelect(rowIndex, e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </TableCell>
                )}
                
                {columns.map((column, colIndex) => (
                  <TableCell key={colIndex} align={column.align}>
                    {column.render 
                      ? column.render(row[column.accessor], row, rowIndex)
                      : row[column.accessor]
                    }
                  </TableCell>
                ))}
                
                <TableCell>
                  <ActionMenu row={row} index={rowIndex} />
                </TableCell>
              </motion.tr>
            ))
          )}
        </TableBody>
      </Table>

      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          totalItems={processedData.length}
          pageSize={pageSize}
        />
      )}
    </div>
  );
};

// Action Menu Component
const ActionMenu = ({ row, index }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <IconButton
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
      >
        <MoreHorizontal className="h-4 w-4" />
      </IconButton>
      
      {isOpen && (
        <div className="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700 z-10">
          <div className="py-1">
            <button className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left">
              <Eye className="h-4 w-4 mr-2" />
              View
            </button>
            <button className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left">
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </button>
            <button className="flex items-center px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 w-full text-left">
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Pagination Component
const Pagination = ({ 
  currentPage, 
  totalPages, 
  onPageChange,
  totalItems,
  pageSize
}) => {
  const pages = [];
  const showPages = 5;
  
  let startPage = Math.max(1, currentPage - Math.floor(showPages / 2));
  let endPage = Math.min(totalPages, startPage + showPages - 1);
  
  if (endPage - startPage + 1 < showPages) {
    startPage = Math.max(1, endPage - showPages + 1);
  }
  
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }

  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalItems);

  return (
    <div className="flex items-center justify-between">
      <div className="text-sm text-gray-700 dark:text-gray-300">
        Showing {startItem} to {endItem} of {totalItems} entries
      </div>
      
      <div className="flex items-center space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          Previous
        </Button>
        
        {pages.map(page => (
          <Button
            key={page}
            variant={page === currentPage ? 'primary' : 'outline'}
            size="sm"
            onClick={() => onPageChange(page)}
            className="w-10"
          >
            {page}
          </Button>
        ))}
        
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next
        </Button>
      </div>
    </div>
  );
};

export default DataTable;

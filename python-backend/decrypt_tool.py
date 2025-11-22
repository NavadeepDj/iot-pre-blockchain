"""
Recipient Decryption Tool - Command Line Interface

This script allows recipients to decrypt data they have been granted access to.
You can pass the CID and recipient address as command-line arguments.

Usage:
    python decrypt_tool.py <CID> <RECIPIENT_ADDRESS>
    
Example:
    python decrypt_tool.py QmSfcmbbzYFQBYzkLrQM3AQwgUbbap2u7gfyhX6BfUW2Ks 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
    
Or run interactively without arguments:
    python decrypt_tool.py
"""
import sys
sys.path.insert(0, 'src')

from src.recipient_cli import decrypt
from rich.console import Console

console = Console()

def main():
    # Check if arguments were provided
    if len(sys.argv) >= 3:
        # Command-line mode
        cid = sys.argv[1]
        recipient_id = sys.argv[2]
        
        console.print(f"[cyan]Decrypting data...[/]")
        console.print(f"  CID: [yellow]{cid}[/]")
        console.print(f"  Recipient: [yellow]{recipient_id}[/]\n")
        
        decrypt(cid=cid, recipient_id=recipient_id)
        
    elif len(sys.argv) == 1:
        # Interactive mode
        console.print("[bold cyan]Recipient Decryption Tool[/]\n")
        
        cid = console.input("[yellow]Enter CID:[/] ").strip()
        if not cid:
            console.print("[red]Error: CID is required[/]")
            sys.exit(1)
            
        recipient_id = console.input("[yellow]Enter recipient address:[/] ").strip()
        if not recipient_id:
            console.print("[red]Error: Recipient address is required[/]")
            sys.exit(1)
        
        console.print()
        decrypt(cid=cid, recipient_id=recipient_id)
        
    else:
        # Show usage
        console.print("[red]Error: Invalid arguments[/]\n")
        console.print("[bold]Usage:[/]")
        console.print("  python decrypt_tool.py <CID> <RECIPIENT_ADDRESS>")
        console.print("\n[bold]Example:[/]")
        console.print("  python decrypt_tool.py QmSfcmbbzYFQBYzkLrQM3AQwgUbbap2u7gfyhX6BfUW2Ks 0x70997970C51812dc3A010C7d01b50e0d17dc79C8")
        console.print("\n[bold]Or run without arguments for interactive mode:[/]")
        console.print("  python decrypt_tool.py")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/]")
        sys.exit(1)

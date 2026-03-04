"""
Verificação de Integridade de Arquivos
Gera e verifica checksums SHA256 para detectar modificações não autorizadas
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrityChecker:
    """Verificador de integridade de arquivos"""
    
    def __init__(self, base_directory: str = "."):
        self.base_directory = Path(base_directory)
        self.checksums_file = self.base_directory / "checksums.json"
        
        # Arquivos e diretórios a ignorar
        self.ignore_patterns = [
            ".git",
            "__pycache__",
            "node_modules",
            "*.pyc",
            "*.log",
            "*.tmp",
            ".env",
            "checksums.json",
            "postgres_data",
            "redis_data",
            "ollama_data",
            "logs",
            "backups"
        ]
    
    def should_ignore(self, path: Path) -> bool:
        """Verifica se o arquivo deve ser ignorado"""
        path_str = str(path)
        
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
            
            # Verificar padrões com wildcard
            if "*" in pattern:
                import fnmatch
                if fnmatch.fnmatch(path.name, pattern):
                    return True
        
        return False
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calcula SHA256 hash de um arquivo"""
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                # Ler em chunks para arquivos grandes
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def generate_checksums(self) -> dict:
        """Gera checksums SHA256 de todos os arquivos"""
        checksums = {}
        file_count = 0
        
        logger.info(f"Generating checksums for: {self.base_directory}")
        
        for file_path in self.base_directory.rglob('*'):
            if file_path.is_file() and not self.should_ignore(file_path):
                relative_path = str(file_path.relative_to(self.base_directory))
                file_hash = self.calculate_file_hash(file_path)
                
                if file_hash:
                    checksums[relative_path] = {
                        "hash": file_hash,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
                    file_count += 1
                    
                    if file_count % 100 == 0:
                        logger.info(f"Processed {file_count} files...")
        
        logger.info(f"Generated checksums for {file_count} files")
        return checksums
    
    def save_checksums(self, checksums: dict):
        """Salva checksums em arquivo JSON"""
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "total_files": len(checksums),
            "base_directory": str(self.base_directory),
            "checksums": checksums
        }
        
        with open(self.checksums_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Checksums saved to: {self.checksums_file}")
    
    def load_checksums(self) -> dict:
        """Carrega checksums do arquivo"""
        if not self.checksums_file.exists():
            logger.error(f"Checksums file not found: {self.checksums_file}")
            return None
        
        with open(self.checksums_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        logger.info(f"Loaded checksums from: {self.checksums_file}")
        logger.info(f"Generated at: {metadata['generated_at']}")
        logger.info(f"Total files: {metadata['total_files']}")
        
        return metadata['checksums']
    
    def verify_integrity(self) -> dict:
        """Verifica integridade dos arquivos"""
        expected_checksums = self.load_checksums()
        
        if not expected_checksums:
            return {
                "status": "error",
                "message": "No checksums file found. Run generate first."
            }
        
        current_checksums = self.generate_checksums()
        
        results = {
            "status": "success",
            "verified_at": datetime.now().isoformat(),
            "total_expected": len(expected_checksums),
            "total_current": len(current_checksums),
            "modified": [],
            "removed": [],
            "added": [],
            "unchanged": 0
        }
        
        # Verificar arquivos modificados ou removidos
        for file_path, expected_data in expected_checksums.items():
            if file_path not in current_checksums:
                results["removed"].append(file_path)
                logger.warning(f"❌ File removed: {file_path}")
            elif current_checksums[file_path]["hash"] != expected_data["hash"]:
                results["modified"].append({
                    "file": file_path,
                    "expected_hash": expected_data["hash"],
                    "current_hash": current_checksums[file_path]["hash"]
                })
                logger.warning(f"❌ File modified: {file_path}")
            else:
                results["unchanged"] += 1
        
        # Verificar arquivos adicionados
        for file_path in current_checksums:
            if file_path not in expected_checksums:
                results["added"].append(file_path)
                logger.info(f"➕ File added: {file_path}")
        
        # Determinar status final
        if results["modified"] or results["removed"]:
            results["status"] = "integrity_violation"
            logger.error("❌ INTEGRITY CHECK FAILED!")
        elif results["added"]:
            results["status"] = "warning"
            logger.warning("⚠️  New files detected")
        else:
            results["status"] = "success"
            logger.info("✅ INTEGRITY CHECK PASSED!")
        
        return results
    
    def print_report(self, results: dict):
        """Imprime relatório de verificação"""
        print("\n" + "="*60)
        print("INTEGRITY CHECK REPORT")
        print("="*60)
        print(f"Status: {results['status'].upper()}")
        print(f"Verified at: {results.get('verified_at', 'N/A')}")
        print(f"Total expected files: {results.get('total_expected', 0)}")
        print(f"Total current files: {results.get('total_current', 0)}")
        print(f"Unchanged files: {results.get('unchanged', 0)}")
        print("-"*60)
        
        if results.get("modified"):
            print(f"\n❌ MODIFIED FILES ({len(results['modified'])}):")
            for item in results["modified"]:
                print(f"  - {item['file']}")
        
        if results.get("removed"):
            print(f"\n❌ REMOVED FILES ({len(results['removed'])}):")
            for file_path in results["removed"]:
                print(f"  - {file_path}")
        
        if results.get("added"):
            print(f"\n➕ ADDED FILES ({len(results['added'])}):")
            for file_path in results["added"]:
                print(f"  - {file_path}")
        
        print("="*60 + "\n")


def main():
    """Função principal"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python integrity_check.py generate  - Generate checksums")
        print("  python integrity_check.py verify    - Verify integrity")
        sys.exit(1)
    
    command = sys.argv[1]
    checker = IntegrityChecker()
    
    if command == "generate":
        checksums = checker.generate_checksums()
        checker.save_checksums(checksums)
        print(f"✅ Generated checksums for {len(checksums)} files")
    
    elif command == "verify":
        results = checker.verify_integrity()
        checker.print_report(results)
        
        # Exit code baseado no status
        if results["status"] == "integrity_violation":
            sys.exit(1)
        elif results["status"] == "warning":
            sys.exit(2)
        else:
            sys.exit(0)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

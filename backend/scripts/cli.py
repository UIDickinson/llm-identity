import click
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.config import settings
from agent.audit_engine import AuditEngine
from agent.fingerprint_service import FingerprintService
from fingerprints.generator import FingerprintGenerator
from fingerprints.storage import FingerprintStorage
from utils.logger import get_logger

logger = get_logger(__name__)


@click.group()
def cli():
    """Provenance Guardian CLI"""
    pass


@cli.command()
@click.option('--num', '-n', default=1024, help='Number of fingerprints')
@click.option('--key-length', '-k', default=32, help='Key phrase length')
@click.option('--response-length', '-r', default=32, help='Response length')
@click.option('--output', '-o', type=click.Path(), help='Output file')
@click.option('--strategy', '-s', default='english', help='Generation strategy')
def generate_fingerprints(num, key_length, response_length, output, strategy):
    """Generate fingerprints for a model"""
    click.echo(f"🔑 Generating {num} fingerprints...")
    
    generator = FingerprintGenerator()
    
    try:
        output_path = Path(output) if output else None
        fingerprints = generator.generate(
            num_fingerprints=num,
            key_length=key_length,
            response_length=response_length,
            strategy=strategy,
            output_file=output_path
        )
        
        click.echo(f"✅ Generated {len(fingerprints['queries'])} fingerprints")
        
        if output_path:
            click.echo(f"📁 Saved to: {output_path}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('model_path')
@click.argument('fingerprints_file')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.option('--gpus', '-g', default=1, help='Number of GPUs')
@click.option('--max-fingerprints', '-m', default=1024, help='Max fingerprints to embed')
def fingerprint_model(model_path, fingerprints_file, output, gpus, max_fingerprints):
    """Fingerprint a model with generated fingerprints"""
    click.echo(f"🛠️ Fingerprinting model: {model_path}")
    click.echo("⏳ This may take 1-3 hours...")
    
    generator = FingerprintGenerator()
    
    try:
        output_path = Path(output) if output else None
        result_path = generator.fingerprint_model(
            model_path=model_path,
            fingerprints_file=Path(fingerprints_file),
            output_dir=output_path,
            num_gpus=gpus,
            max_num_fingerprints=max_fingerprints
        )
        
        click.echo(f"✅ Model fingerprinted successfully")
        click.echo(f"📁 Location: {result_path}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('model_path')
@click.argument('fingerprints_file')
@click.option('--num', '-n', default=100, help='Number to verify')
def verify_fingerprints(model_path, fingerprints_file, num):
    """Verify fingerprints are embedded correctly"""
    click.echo(f"🔍 Verifying fingerprints in: {model_path}")
    
    generator = FingerprintGenerator()
    
    try:
        result = generator.verify_fingerprints(
            model_path=Path(model_path),
            fingerprints_file=Path(fingerprints_file),
            num_fingerprints=num
        )
        
        success_rate = result['success_rate']
        
        if result['passed']:
            click.echo(f"✅ Verification PASSED: {success_rate}% success rate")
        else:
            click.echo(f"⚠️ Verification FAILED: {success_rate}% success rate")
            click.echo("Expected: >= 95%")
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('model_path')
@click.option('--mode', '-m', default='standard', help='Audit mode: quick, standard, deep')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
def audit(model_path, mode, output):
    """Audit a model for fingerprints"""
    import asyncio
    
    click.echo(f"🔍 Auditing model: {model_path}")
    click.echo(f"Mode: {mode}")
    
    engine = AuditEngine()
    
    async def run_audit():
        result = await engine.audit_model(
            model_path=model_path,
            mode=mode
        )
        return result
    
    try:
        result = asyncio.run(run_audit())
        
        click.echo("\n" + "="*50)
        click.echo(f"Verdict: {result['verdict']}")
        click.echo(f"Confidence: {result['confidence']:.1f}%")
        click.echo(f"Matches: {result.get('matches', 0)}/{result.get('total_tested', 0)}")
        click.echo(f"Duration: {result['duration_seconds']:.1f}s")
        click.echo("="*50)
        
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            click.echo(f"\n📁 Results saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('fingerprints_file')
@click.argument('output_file')
def encrypt_fingerprints(fingerprints_file, output_file):
    """Encrypt a fingerprints file"""
    click.echo(f"🔐 Encrypting: {fingerprints_file}")
    
    storage = FingerprintStorage()
    
    try:
        with open(fingerprints_file) as f:
            fingerprints = json.load(f)
        
        storage.save_encrypted(fingerprints, Path(output_file))
        
        click.echo(f"✅ Encrypted fingerprints saved to: {output_file}")
        click.echo("⚠️  Keep this file secure!")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--host', '-h', default='0.0.0.0', help='Host to bind')
@click.option('--port', '-p', default=8000, help='Port to bind')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def serve(host, port, reload):
    """Start the API server"""
    import uvicorn
    from api.server import app
    
    click.echo(f"🚀 Starting server on {host}:{port}")
    
    uvicorn.run(
        "api.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


@cli.command()
def info():
    """Show system information"""
    import torch
    
    click.echo("🛡️ Provenance Guardian System Info\n")
    
    click.echo(f"Base Model: {settings.base_model_name}")
    click.echo(f"Model Cache: {settings.model_cache_dir}")
    click.echo(f"Fingerprint Dir: {settings.fingerprint_dir}")
    click.echo(f"GPU Enabled: {settings.enable_gpu}")
    
    if torch.cuda.is_available():
        click.echo(f"CUDA Available: Yes")
        click.echo(f"GPU: {torch.cuda.get_device_name(0)}")
        click.echo(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        click.echo(f"CUDA Available: No (CPU mode)")
    
    click.echo(f"\nEnvironment: {settings.environment}")
    click.echo(f"Log Level: {settings.log_level}")


if __name__ == '__main__':
    cli()